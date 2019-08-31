import discord
from discord.ext import commands
import conversationSolver
from importlib import reload
from discord.ext.commands import CommandNotFound


# TODO: Make an easily updatable daemon for linux.


def embed_maker(description, title='', err=False):
    if err:
        return discord.Embed(title=title, description=description, colour=0xCC0000,
                             url='https://github.com/bain3/brainBot/#error-codes')
    else:
        return discord.Embed(title=title, description=description, colour=0xffb200)


# Starting bot
chats = {}
dev = False
TOKEN = input('Token: ')
if TOKEN[:3] == 'dev':
    TOKEN = TOKEN[3:]
    dev = True
train = False
responses = False
conversationChannel = None
bot = commands.Bot(command_prefix='c.')
bot.remove_command('help')


# On ready
@bot.event
async def on_ready():
    if dev:
        await bot.change_presence(
            activity=discord.Activity(name="developers", type=2))  # Presence: Listening to developers
    else:
        await bot.change_presence(activity=discord.Activity(name="chats", type=3))  # Presence: Watching chats
    for guild in bot.guilds:
        for channel in guild.channels:
            if channel.type == discord.ChannelType.text:
                chats[guild.id] = [conversationSolver.ChatBot(guild), channel, False]
    print("---------------- READY ----------------")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send(embed=embed_maker('Command not found. Use "c.help for available commands"', 'ERR01', True))
    else:
        raise error


@bot.event
async def on_guild_join(guild):
    # Update the list of chat bots.
    for channel in guild.channels:
        if channel.type == discord.ChannelType.text:
            chats[guild.id] = [conversationSolver.ChatBot(guild), channel, False]


@bot.event
async def on_message(message):
    """
    A function that runs every time a message was received by the bot.
    It check if the author is member of a server. (no=ERR02)
    If it passes then it checks if the message was for the RiveScript bot. (yes=Act as a middle man for it.)
    If the message is not for the RiveScript bot then it processes it as a command. (if the author has admin perms in
    the server)
    :param message:
    :return:
    """
    global chats
    # reply with error message when message.author is discord.User
    if isinstance(message.author, discord.User):
        await message.channel.send(embed=embed_maker("This bot is currently only operational in servers,"
                                                     " not in private channels.", 'ERR02', True))
        print('DM / Known bug: {}, {}'.format(message.channel.type, message.author.name))  # debug
        return
    if message.author != bot.user:
        # if chatbot is turned on, the message is not a command and the channel is correct
        if chats[message.guild.id][2] is True and not message.content.startswith('c.') \
                and message.channel == chats[message.guild.id][1]:
            # Get response from RiveScript
            await message.channel.send(
                embed=embed_maker(chats[message.guild.id][0].get_response(message.content, message.author)))
        elif message.author.guild_permissions.administrator or message.author.id == 430369724275097612:
            await bot.process_commands(message)


@bot.command()
async def ping(ctx):
    """
    A command that says pong.
    :param ctx:
    :return:
    """
    await ctx.send('pong')


@bot.command()
async def start(ctx):
    """
    A command that enables the RiveScript responses for every message in the conversation channel.
    :param ctx:
    :return:
    """
    chats[ctx.guild.id][1] = ctx.channel
    chats[ctx.guild.id][2] = True  # enable chat bot
    await ctx.send(embed=embed_maker('Chat bot activated. I will be talking in {}.'
                                     ' Deactivate with: .stop_responses'.format(chats[ctx.guild.id][1])))


@bot.command()
async def stop(ctx):
    """
    A command that disables the RiveScript responses for every message in the conversation channel.
    :param ctx:
    :return:
    """
    chats[ctx.guild.id][2] = False  # disable chat bot
    await ctx.send(embed=embed_maker('Chat bot deactivated.'))


@bot.command()
async def select_channel(ctx):
    """
    A command for selecting another channel for conversation.
    :param ctx:
    :return:
    """
    chats[ctx.guild.id][1] = ctx.channel  # set the conversation channel to the current channel
    await ctx.send(embed=embed_maker("From now on i'll be talking in this channel."))


@bot.command(pass_context=True)
async def r(ctx):
    """
    A command that resets the whole bot mechanism. Only accessible to me (bain).
    :param ctx:
    :return:
    """
    if ctx.message.author.id == 430369724275097612:  # check if user == bain
        global chats
        reload(conversationSolver)  # Reloads all chat bots and the module
        for guild in bot.guilds:
            chats[guild.id][0] = conversationSolver.ChatBot(guild)
        await ctx.send(embed=embed_maker('chat bot reloaded'))


@bot.command()
async def upload(ctx):
    """
    A command for the uploading of user provided RiveScript.
    :param ctx:
    :return:
    """
    if ctx.message.attachments:  # if message has attachment then download and load it to the guild's chat bot
        await ctx.send(embed=embed_maker('Command received, loading...'))
        await ctx.message.attachments[0].save('servers/rive{}.rive'.format(ctx.guild.id))
        code = chats[ctx.guild.id][0].load_file('servers/rive{}.rive'.format(ctx.guild.id))
        if code[0] == 'ERR00':
            await ctx.send(
                embed=embed_maker('Success! Your file has been loaded up. You can now use it on your server.'))
        elif code[0] == 'ERR01':
            await ctx.send(embed=embed_maker('Could not find the script on my filesystem, try to upload it again.'
                                             ' If the problem persists then notify the developer.', 'ERR03', True))
        elif code[0] == 'ERR02':
            await ctx.send(embed=embed_maker('Caught rive script error in uploaded file: \n{}'.format(code[1]),
                                             'ERR04', True))
    else:
        await ctx.send(embed=embed_maker('Please attach your code to the command in a file.'))


@bot.command()
async def remove(ctx):
    """
    A command for the removal of the user uploaded RiveScript. Also removes the file from the file system.
    :param ctx:
    :return:
    """
    # call the remove function from rive script handler
    code = chats[ctx.guild.id][0].remove_file('servers/rive{}.rive'.format(ctx.guild.id))
    if code == 'ERR00':
        chats[ctx.guild.id][0].reload()  # Reloading the bot
        await ctx.send(embed=embed_maker('Your script has been removed and your bot has been reloaded.'))
    elif code == 'ERR01':
        await ctx.send(embed=embed_maker('Your script was not found and so it was not deleted.', 'ERR05', True))
    elif code == 'ERR02':
        await ctx.send(embed=embed_maker('There was an error while deleting your script.', 'ERR06', True))


@bot.command()
async def remove_default(ctx):
    """
    A command for the removal of the default brain of the RiveScript bot. For users who want the bot to only reply
    with their own responses.
    :param ctx:
    :return:
    """
    chats[ctx.guild.id][0].reload(brain=False)
    code = chats[ctx.guild.id][0].load_file('servers/rive{}.rive'.format(ctx.guild.id))
    if code[0] == 'ERR00':
        await ctx.send(embed=embed_maker('The default brain of the bot has been removed. And your custom script'
                                         ' has been reloaded.'))
    elif code[0] == 'ERR01':
        chats[ctx.guild.id][0].reload()
        await ctx.send(embed=embed_maker("The default brain of the bot could not be removed because you has not "
                                         "uploaded a custom RiveScript file.",
                                         'ERR07', True))
    elif code[0] == 'ERR02':
        await ctx.send(embed=embed_maker('Caught rive script error in uploaded file: \n{}'.format(code[1]),
                                         'ERR04', True))


@bot.command()
async def refresh(ctx):
    """
    A command that resets the RiveBot to default form, but keeps the user uploaded file.
    :param ctx:
    :return:
    """
    global chats
    chats[ctx.guild.id][0].reload()  # reload the chat bot of the guild
    await ctx.send(embed=embed_maker('Bot refreshed'))


@bot.command()
async def load(ctx):
    """
    A very bad solution to loading up files that are already uploaded (basically copied from upload())
    TODO: Make this not so bad.
    :param ctx:
    :return:
    """
    code = chats[ctx.guild.id][0].load_file('servers/rive{}.rive'.format(ctx.guild.id))
    if code[0] == 'ERR00':
        await ctx.send(
            embed=embed_maker('Success! Your file has been loaded up. You can now use it on your server.'))
    elif code[0] == 'ERR01':
        await ctx.send(embed=embed_maker('Could not find the script on my filesystem, try the upload it again.'
                                         ' If the problem persists then notify the developer.', 'ERR03', True))
    elif code[0] == 'ERR02':
        await ctx.send(embed=embed_maker('Caught rive script error in uploaded file: \n{}'.format(code[1]),
                                         'ERR04', True))


@bot.command()
async def help(ctx):
    """
    Displaying of the help message nothing more nothing less
    :param ctx:
    :return:
    """
    icnurl = "https://cdn.discordapp.com/avatars/530381879916888065/6c80ee29b6d20adb223a25806e8b29d3.png"
    embedmsg = discord.Embed(
        title='Help / About',
        description="Hello! I'm brainBot, i was made by bain#5038. I'm currently under heavy development so if you "
                    "find any bugs please report them to bain on discord. I am powered by rivescript, the easy to "
                    "code chatbot platform. Please visit [www.rivescript.com](www.rivescript.com) for more info on to "
                    "how to program your own brain.",
        colour=0xffb200
    )
    embedmsg.set_footer(text='bain#5038')
    embedmsg.set_author(name='brainBot', icon_url=icnurl, url='https://github.com/bain3/brainBot')
    embedmsg.add_field(name='c.help', value='Shows this message', inline=True)
    embedmsg.add_field(name='c.start', value='Starts the chat.', inline=True)
    embedmsg.add_field(name='c.stop', value='Stops the chat', inline=True)
    embedmsg.add_field(name='c.select_channel', value='Selects current channel for conversation.', inline=True)
    embedmsg.add_field(name='c.upload',
                       value='Upload your own RiveScript file to the bot. Attach the file to the command.', inline=True)
    embedmsg.add_field(name='c.remove', value='Removes the user uploaded file from the bot.', inline=True)
    embedmsg.add_field(name='c.remove_default', value="Remove the default brain of the bot.", inline=True)
    embedmsg.add_field(name='c.refresh', value="Restore the default settings of the bot.", inline=True)
    embedmsg.add_field(name='c.load', value="Load up your uploaded RiveScript.", inline=True)

    await ctx.send(embed=embedmsg)


bot.run(TOKEN)

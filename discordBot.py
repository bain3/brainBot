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
try:
    with open('token.txt') as f:
        TOKEN = f.read()
except FileNotFoundError:
    TOKEN = input('Token: ')

if TOKEN[:3] == 'dev':
    TOKEN = TOKEN[3:]
    dev = True
train = False
responses = False
conversationChannel = None
bot = commands.Bot(command_prefix=commands.when_mentioned_or('c.'))
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
                break
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

    :param message: The message
    :return: None
    """
    global chats
    if message.author.bot:  # protection from bots
        return
    # reply with error message when message.author is discord.User
    if isinstance(message.author, discord.User):
        if not message.author.discriminator == '0000':
            await message.channel.send(embed=embed_maker("This bot is currently only operational in servers,"
                                                         " not in private channels.", 'ERR02', True))
        return
    if message.author != bot.user:  # protection from itself
        # if chatbot is turned on, the message is not a command and the channel is correct
        if chats[message.guild.id][2] is True and not message.content.startswith('c.') \
                and message.channel == chats[message.guild.id][1]:
            # Get response from RiveScript
            await message.channel.send(
                embed=embed_maker(chats[message.guild.id][0].get_response(message.content, message.author)))
        elif message.author.guild_permissions.administrator or message.author.id == 430369724275097612:
            await bot.process_commands(message)


@bot.command(hidden=True)
async def ping(ctx):
    """
    A command that says pong.

    :param ctx: The context
    :return: None
    """
    await ctx.send('pong')


@bot.command(help='Starts the chat.')
async def start(ctx):
    """
    A command that enables the RiveScript responses for every message in the conversation channel.

    :param ctx: The context
    :return: None
    """
    chats[ctx.guild.id][1] = ctx.channel
    chats[ctx.guild.id][2] = True  # enable chat bot
    await ctx.send(embed=embed_maker('Chat bot activated. I will be talking in {}.'
                                     ' Deactivate with: c.stop'.format(chats[ctx.guild.id][1])))


@bot.command(help='Stops the chat')
async def stop(ctx):
    """
    A command that disables the RiveScript responses for every message in the conversation channel.

    :param ctx: The context
    :return: None
    """
    chats[ctx.guild.id][2] = False  # disable chat bot
    await ctx.send(embed=embed_maker('Chat bot deactivated.'))


@bot.command(help='Selects current channel for conversation.')
async def select_channel(ctx):
    """
    A command for selecting another channel for conversation.

    :param ctx: The context
    :return: None
    """
    chats[ctx.guild.id][1] = ctx.channel  # set the conversation channel to the current channel
    await ctx.send(embed=embed_maker("From now on i'll be talking in this channel."))


@bot.command(hidden=True)
async def r(ctx):
    """
    A command that resets the whole bot mechanism. Only accessible to me (bain).

    :param ctx: THe context
    :return: None
    """
    if await bot.is_owner(ctx.message.author):  # check if user is the owner of this bot
        global chats
        reload(conversationSolver)  # Reloads all chat bots and the module
        for guild in bot.guilds:
            chats[guild.id][0] = conversationSolver.ChatBot(guild)
        await ctx.send(embed=embed_maker('chat bot reloaded'))


@bot.command(help='Upload your own RiveScript file to the bot. Attach the file to the command.')
async def upload(ctx):
    """
    A command for the uploading of user provided RiveScript.

    :param ctx: The context
    :return: None
    """
    if ctx.message.attachments:  # if message has attachment then download and load it to the guild's chat bot
        await ctx.send(embed=embed_maker('Command received, downloading...'))
        await ctx.message.attachments[0].save('servers/rive{}.rive'.format(ctx.guild.id))
        await ctx.invoke(load)
    else:
        await ctx.send(embed=embed_maker('Please attach your code to the command in a file.'))


@bot.command(help='Removes the user uploaded file from the bot.')
async def remove(ctx):
    """
    A command for the removal of the user uploaded RiveScript. Also removes the file from the file system.

    :param ctx: The context
    :return: None
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


@bot.command(help="Remove the default brain of the bot.")
async def remove_default(ctx):
    """
    A command for the removal of the default brain of the RiveScript bot. For users who want the bot to only reply
    with their own responses.

    :param ctx: The context
    :return: None
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


@bot.command(help="Restore the default settings of the bot.")
async def refresh(ctx):
    """
    A command that resets the RiveBot to default form, but keeps the user uploaded file.

    :param ctx: The context
    :return: None
    """
    global chats
    chats[ctx.guild.id][0].reload()  # reload the chat bot of the guild
    await ctx.send(embed=embed_maker('Bot refreshed'))


@bot.command(hidden=True)
async def ls(ctx):
    """
    A command that shows all the servers that the bot is on. Can only be run by the bot owner.

    :param ctx: The context
    :return: None
    """
    if await bot.is_owner(ctx.message.author):
        fields = 0
        embed = discord.Embed(title='All servers')
        for g in chats:
            guild = bot.get_guild(g)
            if fields >= 25:
                await ctx.send(embed=embed)
                embed = discord.Embed()
                fields = 0
            if chats[g][2] is True:
                value = '✅ The chat bot is activated.'
            else:
                value = '❌ The chat bot is disabled.'
            embed.add_field(name=guild.name, value=value)
            fields += 1

        embed.set_footer(text='This bot is in '+str(len(bot.guilds))+' servers.')
        await ctx.send(embed=embed)


@bot.command(help="Load up your uploaded RiveScript.")
async def load(ctx):
    """
    Loading up files, used by the upload command.

    :param ctx: The context
    :return: None
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


@bot.command(help='Shows this message.')
async def help(ctx):
    """
    Displaying of the help message nothing more nothing less.
    """
    icnurl = "https://cdn.discordapp.com/avatars/530381879916888065/6c80ee29b6d20adb223a25806e8b29d3.png"
    embedmsg = discord.Embed(
        title='Help / About',
        description="Hello! I'm brainBot."
                    "I'm currently under heavy development so if you find any bugs please report them in "
                    "the [support server](https://discord.gg/y5b7U5U). I am powered by rivescript, "
                    "the easy to code chatbot platform. "
                    "Please visit [rivescript.com](http://www.rivescript.com) for more info on to how to program your "
                    "own brain.",
        colour=0xffb200
    )
    embedmsg.set_author(name='brainBot', icon_url=icnurl, url='https://github.com/bain3/brainBot')
    for command in bot.walk_commands():
        if command.hidden is not True:
            embedmsg.add_field(name=command.name, value=command.help)

    await ctx.send(embed=embedmsg)


bot.run(TOKEN)

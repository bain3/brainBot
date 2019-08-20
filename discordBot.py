import discord
from discord.ext import commands
import conversationSolver
from importlib import reload

TOKEN = input('Token: ')


def embed_maker(description, title=''):
    return discord.Embed(title=title, description=description, colour=0xffb200)


# Starting bot
chats = {}
train = False
responses = False
conversationChannel = None
bot = commands.Bot(command_prefix='.')
bot.remove_command('help')


# On ready
@bot.event
async def on_ready():
    for guild in bot.guilds:
        for channel in guild.channels:
            if channel.type == discord.ChannelType.text:
                chats[guild.id] = [conversationSolver.ChatBot(guild), channel, False]
    print("---------------- READY ----------------")


@bot.event
async def on_guild_join(guild):
    for channel in guild.channels:
        if channel.type == discord.ChannelType.text:
            chats[guild.id] = [conversationSolver.ChatBot(guild), channel, False]


@bot.event
async def on_message(message):
    global chats
    # if chatbot is turned on, the message is not a command and the channel is correct
    if chats[message.guild.id][2] is True and not message.content.startswith('.') \
            and message.channel == chats[message.guild.id][1]:
        if message.author != bot.user:
            await message.channel.send(
                embed=embed_maker(chats[message.guild.id][0].get_response(message.content, message.author)))
    elif message.author.id == message.guild.owner_id:
        try:
            await bot.process_commands(message)
        except discord.ext.commands.errors:
            await message.channel.send(embed=embed_maker('command not found'))


@bot.command(pass_context=True)
async def ping(ctx):
    await ctx.send('pong')


@bot.command(pass_context=True)
async def start_chat(ctx):
    global chats
    chats[ctx.guild.id][2] = True
    await ctx.send(embed=embed_maker('Chat bot activated. It will be talking in {}.'
                                     ' Deactivate with: .stop_responses'.format(chats[ctx.guild.id][1])))


@bot.command(pass_context=True)
async def stop_chat(ctx):
    global chats
    chats[ctx.guild.id][2] = False
    await ctx.send(embed=embed_maker('Chat bot deactivated.'))


@bot.command(pass_context=True)
async def select_channel(ctx):
    global chats
    chats[ctx.guild.id][1] = ctx.channel
    await ctx.send(embed=embed_maker("From now on i'll be talking in this channel."))


@bot.command(pass_context=True)
async def r(ctx):
    if ctx.message.author.id == 430369724275097612:
        global chats
        reload(conversationSolver)
        for guild in bot.guilds:
            chats[guild.id][0] = conversationSolver.ChatBot(guild)
        await ctx.send(embed=embed_maker('chat bot reloaded'))


@bot.command(pass_context=True)
async def upload(ctx):
    global chats
    if ctx.message.attachments:
        await ctx.send(embed=embed_maker('Command received, loading...'))
        await ctx.message.attachments[0].save('servers/rive{}.rs'.format(ctx.guild.id))

        await ctx.send(
            embed=embed_maker(chats[ctx.guild.id][0].load_guild_file('servers/rive{}.rs'.format(ctx.guild.id))))
    else:
        await ctx.send(embed=embed_maker('Please attach your code to the command in a file.'))


@bot.command(pass_context=True)
async def reload_bot(ctx):
    global chats
    chats[ctx.guild.id][0].reload()
    chats[ctx.guild.id][0].load_guild_file('servers/rive{}.rs'.format(ctx.guild.id))
    await ctx.send(embed=embed_maker('Bot reloaded'))


@bot.command(pass_context=True)
async def help(ctx):
    embedmessage = discord.Embed(
        title='Help / About',
        description="Hello! I'm brainBot, i was made by bain#5038. I'm currently under heavy development so if you "
                    "find any bugs please report them to bain on discord. I am powered by rivescript, the easy to "
                    "code chatbot platform. Please visit [www.rivescript.com](www.rivescript.com) for more info on to "
                    "how to program your own brain.",
        colour=0xffb200
    )
    embedmessage.set_footer(text='bain#5038')
    embedmessage.set_author(name='brainBot',
                            icon_url='https://cdn.discordapp.com/avatars/530381879916888065'
                                     '/3aea2442c56d5af592ef11d68e20bb32.png')
    embedmessage.add_field(name='.help', value='Shows this message', inline=True)
    embedmessage.add_field(name='.start_chat', value='Starts the chat.', inline=False)
    embedmessage.add_field(name='.stop_chat', value='Stops the chat', inline=True)
    embedmessage.add_field(name='.select_channel', value='Selects current channel for conversation.', inline=False)
    embedmessage.add_field(name='.upload',
                           value='Add your own rive script. Attach the rivescript file to this message.', inline=True)
    embedmessage.add_field(name='.reload_bot', value="Reload your bot.", inline=True)

    await ctx.send(embed=embedmessage)
bot.run(TOKEN)

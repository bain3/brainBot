### brainBot
A discord bot that can download and run custom rivescripts for each server. To create your own
rive script head on to www.rivescript.com.

#### Commands
##### .help
Shows help message
##### .start_chat
Starts the RiveScript chat bot. It will only talk in the selected channel. (to select a channel
use .select_channel)
##### .stop_chat
Stops the RiveScript chat bot.
##### .select_channel
Select the current channel for the conversation.
##### .upload
Upload your own RiveScript file to the bot. Attach the file to the command.
##### .reload_bot
Reload the chat bot for your server.

#### [Add it to your server](https://discordapp.com/oauth2/authorize?client_id=530381879916888065&permissions=130112&scope=bot)

#### Error Codes

##### ERR01
The command your entered was not found.

##### ERR02
Talking in DM channels is not supported.

It is possible that the bot could not indentify the server you we're talking in.

##### ERR03
The bot could not find the file downloaded to the file system.

##### ERR04
An error was caught from rive script while loading the user uploaded script. Please check your
script for syntax errors. To test your script in real time use: [play.rivescript.com](https://play.rivescript.com/)

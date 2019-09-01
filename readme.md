### [brainBot (click to add)](https://discordapp.com/oauth2/authorize?client_id=530381879916888065&permissions=130112&scope=bot)
A discord bot that can download and run custom rivescripts for each server. To create your own
rive script head on to www.rivescript.com.

#### Commands
##### c.help
Shows help message
##### c.start
Starts the RiveScript chat bot. It will only talk in the selected channel. (to select a channel
use c.select_channel)
##### c.stop
Stops the RiveScript chat bot.
##### c.select_channel
Select the current channel for the conversation.
##### c.upload
Upload your own RiveScript file to the bot. Attach the file to the command.
##### c.remove
Removes the user uploaded file from the bot.
##### c.remove_default
Remove the default brain of the bot.
##### c.refresh
Restore the default settings of the bot.
##### c.load
Load up your uploaded RiveScript file.

#### Error Codes

##### ERR01
The command your entered was not found. [All the commands](https://github.com/bain3/brainBot/#commands)

##### ERR02
Talking in DM channels is not supported.

It is possible that the bot could not indentify the server you we're talking in. In that case please contact the bot's 
developer.

##### ERR03
The file was not found in the file system and so it was not loaded.

##### ERR04
An error was caught from rive script while loading the user uploaded script. Please check your
script for syntax errors. To test your script in real time use: 
[play.rivescript.com](https://play.rivescript.com/)

##### ERR05
The file was not found in the file system so it was not deleted. Either the administrator of the bot has removed it or 
you have already deleted it before.

##### ERR06
There was an error while removing the file.

##### ERR07
The default brain of the bot was not removed because the user has not uploaded a RiveScript file. This action is 
necessary to not have errors all over the place.

# Clarity Bot

Clarity is a discord bot coded in python using the discord.py library along with other various libraries and api's

It comes with a group of commands called raffle which are created using OOP and the raffle.py file:
+raffle list prints a list of all the existing raffles
+raffle create [name] creates a raffle of [name] if it does not exist
+raffle join [name] lets you join a raffle of [name] as long as it exists
+raffle leave [name] lets you leave a raffle that you previously joined
+raffle start [name] lets you start a raffle (only if you are the raffle creator)
+raffle disband [name] lets you disband a raffle (only if you are the creator, or an admin
+raffle info [name] provides info on who is in the following raffle


## Notes

To run this bot on your own machine, you need to install the following libraries:

pip install -U python-dotenv
pip install discord.py
pip install pyjokes

You also would need your own .env file that has a token connecting to your own discord bot. 

Learn how to make a discord bot here. 
https://realpython.com/how-to-make-a-discord-bot-python/#how-to-make-a-discord-bot-in-the-developer-portal

Once you do that, and retrieve a bot token, you can set DISCORD_TOKEN=(token) in your   .env file. 

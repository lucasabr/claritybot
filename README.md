# Clarity Bot
Author: Lucas Aguiar

Clarity is a discord bot coded in python using the discord.py library along with other various libraries and api's

Clarity is mostly error free and I am actively working on finding and catching errors as well as adding features 

It comes with a group of commands called raffle which are created using OOP and the raffle.py file:

+raffle list prints a list of all the existing raffles in the guild

+raffle create [name] creates a raffle of [name] if it does not exist

Joining and leaving a raffle is done by reacting to the raffle message (which is created and pinned by the bot) with :sunglasses:

+raffle start [name] lets you start a raffle (only if you are the raffle creator)

+raffle disband [name] lets you disband a raffle (only if you are the creator, or an admin

It also comes along with two smaller commands:

+joke sends a random joke from the pyjokes library

+randomnum [min] [max] chooses a random number from [min] to [max]

+randomnum nm [max] chooses a random number from 0 to [max] or [max] to 0 depending on if max is negative or positive.


## Notes

To run this bot on your own machine, you need to install the following libraries:

pip install -U python-dotenv
pip install discord.py
pip install pyjokes

You also would need your own .env file that has a token connecting to your own discord bot. 

Learn how to make a discord bot here. 
https://realpython.com/how-to-make-a-discord-bot-python/#how-to-make-a-discord-bot-in-the-developer-portal

Once you do that, and retrieve a bot token, you can set DISCORD_TOKEN=(token) in your   .env file. 

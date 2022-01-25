import os
import random


import discord
import pyjokes
import raffle
import pip._vendor.requests as requests
import yfinance as yf
import sys
import traceback

from discord.ext import commands
from dotenv import load_dotenv
from raffle import Raffle

#Create's a bot and connects this file to the bot via discord_token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='+', help_command=None)

raffleList = []


@bot.event
async def on_ready():
    print('Working') #Prints 'working' in console once the bot is launched.
    
# Help Command that showcases all the possible commands or groups of commands
@bot.command()
async def help(context):
    embed=discord.Embed(title="Help", description='Here is a list of all the possible commands', color=discord.Color.gold())
    embed.add_field(name="+joke", value="This command sends a random joke using the pyjokes library", inline=False)
    embed.add_field(name="+raffle", value="Group of commands that involve raffles", inline=False)
    embed.add_field(name="+finance", value="Group of commands that involve stocks and finance", inline=False)
    embed.add_field(name="+github", value="Group of commands that involve github", inline=False)
    embed.add_field(name="+randomnum [min] [max]", value="Chooses a random number from [min] to [max].")
    embed.add_field(name="+randomnum nm [max]", value="Chooses a random number from 0 to [max].")
    await context.send(embed=embed)

#Error handling for a command that does not exist. Ex: if one were to enter "+test" 
@bot.event
async def on_command_error(context, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        embed=discord.Embed(title="ERROR!", description="This command does not exist.\nPlease do +help to see the list of commands.",
        color=discord.Color.red())
        await context.send(embed=embed)

# Utilizes the pyjokes library to provide a random joke
@bot.command(name='joke')
async def getJoke(context):
    embed=discord.Embed(title="Random Joke", description=pyjokes.get_joke(), color=discord.Color.green())
    await context.send(embed=embed)

#Obtains a random number from min - max
@bot.group(name='randomnum', invoke_without_command=True)
async def randomNumberGenerator(context, min: int, max: int):
    #if the max number is not larger than min number, throws an error
    if(max<=min):
        embed=discord.Embed(title="ERROR!", description="Max must be larger than min!",
        color=discord.Color.red())
        await context.send(embed=embed)
    else:   
        randomNum = random.randint(min, max)
        embed=discord.Embed(title=f'Random Number from {min} to {max}', description=f'The number chosen is: {randomNum}', color=discord.Color.purple())
        await context.send(embed=embed)

#Obtains a random number from 0 - max
@randomNumberGenerator.command(name='nm')
async def randomNoMin(context, max: int):
    #Throws an error if max is zero
    if(max==0):
        embed=discord.Embed(title="ERROR!", description="Max cannot be zero",
        color=discord.Color.red())
        await context.send(embed=embed)
    #Checks if max is less than or greater than 0 in order to randomize the number in the correct way.
    if(max>0):
        randomNum = random.randint(0, max)
        embed=discord.Embed(title=f'Random Number from 0 to {max}', description=f'The number chosen is: {randomNum}', color=discord.Color.purple())
        await context.send(embed=embed)
    else:
        randomNum = random.randint(max, 0)
        embed=discord.Embed(title=f'Random Number from 0 to {max}', description=f'The number chosen is: {randomNum}', color=discord.Color.purple())
        await context.send(embed=embed)

# Raffle Group of commands
# The +raffle command showcases all the possible commands
# Raffle commands utilize the raffle object in raffle.py
@bot.group(name='raffle', invoke_without_command=True)
async def raffleCmd(context):
    embed=discord.Embed(title="Raffle", description="The Raffle Command has many subcommands", color=discord.Color.blue())
    embed.add_field(name='+raffle list', value='Prints a list of all the existing raffles', inline=False)
    embed.add_field(name='+raffle create [name]', value='Creates a raffle of [name] if it does not exist', inline=False)
    embed.add_field(name='+raffle start [name]', value='Lets you start a raffle (only if you are the raffle creator)', inline=False)
    embed.add_field(name='+raffle disband [name]', value='Lets you disband a raffle (only if you are the creator, or an admin)', inline=False)
    await context.send(embed=embed)

# Raffle list command
@raffleCmd.command(name='list')
async def raffleListCmd(context):
    #If raffleList is empty, throws an error
    if not raffleList:
        embed=discord.Embed(title="ERROR!", description="There are currently no existing raffles",
        color=discord.Color.red())
        await context.send(embed=embed)
    #Iterates through raffleList and adds all raffles that are made in this guild to an embed
    else:
        i=1
        empty=True
        for x in raffleList:
            if(x.guild == context.guild.id):
                empty=False
                if(i==1):
                    embed=discord.Embed(title="Raffle List", description="Here are all of the existing raffles",
                    color=discord.Color.blue())
                message = await (x.channel).fetch_message(x.message)
                embed.add_field(name=f'Raffle #{i}', value=f'[{x.name}]({message.jump_url} \"Hovertext\") created by {x.author}', inline=False)  
                i = i+1
        if not empty:   
            await context.send(embed=embed)
        #If there are no raffles from this guild, throws an error
        else:
            embed=discord.Embed(title="ERROR!", description="There are currently no existing raffles",
            color=discord.Color.red())
            await context.send(embed=embed)   

# Raffle create command and error handling below
@raffleCmd.command(name='create')
async def raffleCreate(context, name):
    # If there is no existing raffle in this guild with the given name
    # Then it creates a new raffle object, sends an embed in the chat, pins it and auto adds the required reaction to join the raffle 
    if(contains(name, context.guild.id)==False):
        embed=discord.Embed(title="Raffle Created!", description=f'{name} has been created by {context.author.mention}!\nReact with :sunglasses: to join',
        color=discord.Color.blue()) 
        message = await context.send(embed=embed)
        raffleList.append(Raffle(context.author.name, name, message.id, context.guild.id, context.channel))
        message = await (context.channel).fetch_message(message.id)
        await message.pin()
        await message.add_reaction('\U0001f60e')
    # if there is an existing raffle in the guild with the given name, throws an error
    else:
        embed=discord.Embed(title="ERROR!", description="The following raffle already exists. Please create a raffle with a new name or delete the following raffle",
        color=discord.Color.red())
        await context.send(embed=embed)

@raffleCreate.error
async def create_error(context, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        embed=discord.Embed(title="ERROR!", description="A name is required for this command! Try again.",
        color=discord.Color.red())
        await context.send(embed=embed)
    elif isinstance(error, discord.ext.commands.errors.UnexpectedQuoteError):
        embed=discord.Embed(title="ERROR!", description="You cannot include quotations in your raffle name.",
        color=discord.Color.red())
        await context.send(embed=embed)
    else:
        print('Ignoring exception in command {}:'.format(context.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr) 

# Raffle start command and error handling
@raffleCmd.command(name='start')
async def raffleStart(context, name):
    # if there is no raffle with this name in the server, throws error
    if(contains(name, context.guild.id)==False):
        embed=discord.Embed(title="ERROR!", description="This raffle does not exist!",
        color=discord.Color.red())
        await context.send(embed=embed)
    else:
        temp = find(name, context.guild.id)
        # Catches discord.NotFound error if the raffle message was deleted
        try:
            message = await (temp.channel).fetch_message(temp.message)
        except discord.NotFound:
            embed=discord.Embed(title="ERROR!", description="Looks like the raffle message was deleted.\nDisband the raffle and create a new one.",
            color=discord.Color.red())
            await context.send(embed=embed)
        else:
            #if the user doing the command was not the raffle author, throws an error
            await message.remove_reaction('\U0001f60e', bot.user)
            if(context.author.name != find(name, context.guild.id).author):
                await message.add_reaction('\U0001f60e')
                embed=discord.Embed(title="ERROR!", description="You are not the creator of this raffle and cannot start it",
                color=discord.Color.red())
                await context.send(embed=embed)
            else:
                #iterates through an array of reactions looking for the :sunglasses: reaction by unicode
                #if it finds the reaction, then it uses the .users() coro to get an array of all the users that reacted with that emoji
                #and then picks a raffle winner
                unempty=True
                await message.unpin()
                message = await (temp.channel).fetch_message(temp.message)
                reactions = message.reactions
                if(len(reactions)==0):
                    unempty=False
                else:
                    unempty = False
                    reaction = reactions[0]
                    for r in reactions:
                        if r.emoji == '\U0001f60e':
                            reaction = r
                            unempty = True
                if unempty:
                    users = await reaction.users().flatten()
                    winner = random.choice(users)
                    raffleList.remove(temp)
                    temp.author = None
                    embed=discord.Embed(title="Raffle Results!", description=f'Congrats to {winner.mention} for winning the raffle', color=discord.Color.blue())
                    await context.send(embed=embed)
                #if nobody reacted with the sunglasses emoji, throws an error
                else: 
                    await message.add_reaction('\U0001f60e')
                    embed=discord.Embed(title="ERROR!", description="There is nobody in this raffle.",
                    color=discord.Color.red())
                    await context.send(embed=embed)

@raffleStart.error
async def start_error(context, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        embed=discord.Embed(title="ERROR!", description="A name is required for this command! Try again.",
        color=discord.Color.red())
        await context.send(embed=embed)   
    else:
        print('Ignoring exception in command {}:'.format(context.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

# Raffle disband command and error handling
@raffleCmd.command(name='disband')
async def raffleDisband(context, name):
    # if there is no raffle in the guild with this name, throws error
    if(contains(name, context.guild.id)==False):
        embed=discord.Embed(title="ERROR!", description="This raffle does not exist!",
        color=discord.Color.red())
        await context.send(embed=embed)
    # if the user calling the command is not the raffle author or an administrator, throws an error
    elif((context.author.name != find(name, context.guild.id).author) and (context.author.guild_permissions.administrator == False)):
        embed=discord.Embed(title="ERROR!", description="You are not the creator of this raffle nor are you an admin and cannot disband it.",
        color=discord.Color.red())
        await context.send(embed=embed)
    #Otherwise disbands and deletes the raffle object
    else:
        embed=discord.Embed(title="Raffle Disbanded", description=f'Raffle {name} successfully disbanded',
        color=discord.Color.blue()) 
        await context.send(embed=embed)
        correctRaffle = find(name, context.guild.id)
        raffleList.remove(correctRaffle)
        correctRaffle.entries.clear()
        correctRaffle.author = None

@raffleDisband.error
async def disband_error(context, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        embed=discord.Embed(title="ERROR!", description="A name is required for this command! Try again.",
        color=discord.Color.red())
        await context.send(embed=embed)
    else:
        print('Ignoring exception in command {}:'.format(context.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

# Finance Group of commands
# The +finance command showcases all the possible commands
@bot.group(name='finance', invoke_without_command=True)
async def financeCmd(context):
    embed=discord.Embed(title="Finance", description="The Finance Command has many subcommands", color=discord.Color.purple())
    embed.add_field(name='+finance price [TICKER]', value='Shows the current price of the stock', inline=False)
    embed.add_field(name='+finance info [TICKER]', value='Gives a basic overview of the company', inline=False)
    embed.add_field(name='+finance quote [TICKER]', value='Shows basic statistics about the stock', inline=False)
    await context.send(embed=embed)

@financeCmd.command(name='price')
async def getPrice(context, ticker):
    stock = yf.Ticker(ticker).info
    print(stock)
    currency = stock['currency']
    price = stock['currentPrice']
    name = stock['longName']
    img = stock['logo_url']
    embed=discord.Embed(title=name + " [" + (str)(ticker) + "]", description=currency + " $" + (str)(price), color=discord.Color.purple())
    embed.set_thumbnail(url=img)
    await context.send(embed=embed)

@getPrice.error
async def getPrice_error(context, error):
    embed=discord.Embed(title="ERROR", description="Something went wrong! Make sure the ticker you provided is valid", color=discord.Color.red())
    print(error)
    await context.send(embed=embed)

@financeCmd.command(name='info')
async def getInfo(context, ticker):
    stock = yf.Ticker(ticker).info
    summary = stock['longBusinessSummary']
    name = stock['longName']
    img = stock['logo_url']
    embed=discord.Embed(title=name + " [" + (str)(ticker) + "]", description=summary, color=discord.Color.purple())
    embed.set_thumbnail(url=img)
    await context.send(embed=embed)

@getInfo.error
async def getInfo_error(context, error):
    embed=discord.Embed(title="ERROR", description="Something went wrong! Make sure the ticker you provided is valid", color=discord.Color.red())
    print(error)
    await context.send(embed=embed)

@financeCmd.command(name='quote')
async def getQuote(context, ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    currency = info['currency']
    price = info['currentPrice']
    name = info['longName']
    img = info['logo_url']
    embed=discord.Embed(title=name + " [" + (str)(ticker) + "]", color=discord.Color.purple())
    embed.add_field(name="Price", value=currency + " $" + (str)(price), inline=False)


    fiftytwoweeklow = currency + " $" + str(info['fiftyTwoWeekLow'])
    fiftytwoweekhigh = str(info['fiftyTwoWeekHigh'])
    daylow = currency + " $" + str(info['dayLow'])
    dayhigh = str(info['dayHigh'])
    
    embed.add_field(name="Day's Range", value=daylow + " - " + dayhigh)
    embed.add_field(name="52 Week Range", value=fiftytwoweeklow + " - " + fiftytwoweekhigh)

    try:
        marketcap = info['marketCap']
        marketcap = format_num(marketcap)
        embed.add_field(name="Market Cap", value=marketcap, inline=False)
    except KeyError:
        print("No marketcap")

    try:
        pe = info['trailingPE']
        embed.add_field(name="PE", value=round(pe, 2), inline=False)
    except KeyError:
        print("No PE ratio")

    try: 
        dividendRate = info['dividendRate']
        if(isinstance(dividendRate, float)):
            dividendYield = round((float(dividendRate)/float(price)) * 100, 2)
            embed.add_field(name="Dividend Rate", value=dividendRate, inline=False)
            embed.add_field(name="Dividend Yield", value=dividendYield, inline=False)
    except KeyError:
        print("No Dividend")

    try:
        eps = info['trailingEps']
        embed.add_field(name="Earnings Per Share", value=round(eps, 2), inline=False)
    except KeyError:
        print("No EPS")
    
    try:
        beta = info['beta']
        embed.add_field(name="Beta", value=round(beta, 2), inline=False)
    except KeyError:
        print("No Beta")

    embed.set_thumbnail(url=img)
    await context.send(embed=embed)


@getQuote.error
async def getQuote_error(context, error):
    embed=discord.Embed(title="ERROR", description="Something went wrong! Make sure the ticker you provided is valid", color=discord.Color.red())
    print(error)
    await context.send(embed=embed)

# Finds the correct raffle by name in the raffleList
def find(name, guild):
    for x in raffleList:
        if(name==x.name and guild==x.guild):
            return x 
# Checks to see if a raffle exists in the raffleList
def contains(name, guild):
    value = False
    for x in raffleList:
        if(name==x.name and guild==x.guild):
            value = True
    return value

#formats numbers for market cap
def format_num(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'K', 'M', 'B', 'T'][magnitude])

#runs the bot
bot.run(TOKEN)

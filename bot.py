import os
import random


import discord
import pyjokes
import raffle

from discord.ext import commands
from dotenv import load_dotenv
from raffle import Raffle

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='+', help_command=None)

raffleList = []

@bot.event
async def on_ready():
    print('Working')
    
# Help Command that showcases all the possible commands or groups of commands
@bot.command()
async def help(context):
    embed=discord.Embed(title="Help", description='Here is a list of all the possible commands', color=discord.Color.gold())
    embed.add_field(name="+joke", value="This command sends a random joke using the pyjokes library", inline=False)
    embed.add_field(name="+raffle", value="Group of commands that involve raffles", inline=False)
    embed.add_field(name="+randomnum [min] [max]", value="Chooses a random number from [min] to [max].")
    embed.add_field(name="+randomnum nm [max]", value="Chooses a random number from 0 to [max].")
    await context.send(embed=embed)

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

@bot.group(name='randomnum', invoke_without_command=True)
async def randomNumberGenerator(context, min: int, max: int):
    randomNum = random.randint(min, max)
    embed=discord.Embed(title=f'Random Number from {min} to {max}', description=f'The number chosen is: {randomNum}', color=discord.Color.purple())
    await context.send(embed=embed)

@randomNumberGenerator.command(name='nm')
async def randomNoMin(context, max: int):
    randomNum = random.randint(0, max)
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
    if not raffleList:
        embed=discord.Embed(title="ERROR!", description="There are currently no existing raffles",
        color=discord.Color.red())
        await context.send(embed=embed)
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
        else:
            embed=discord.Embed(title="ERROR!", description="There are currently no existing raffles",
            color=discord.Color.red())
            await context.send(embed=embed)   

# Raffle create command and error handling below
@raffleCmd.command(name='create')
async def raffleCreate(context, name):
    if(contains(name, context.guild.id)==False):
        embed=discord.Embed(title="Raffle Created!", description=f'{name} has been created by {context.author.mention}!\nReact with :sunglasses: to join',
        color=discord.Color.blue()) 
        message = await context.send(embed=embed)
        raffleList.append(Raffle(context.author.name, name, message.id, context.guild.id, context.channel))
        message = await (context.channel).fetch_message(message.id)
        await message.pin()
        await message.add_reaction('\U0001f60e')
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
        
# Raffle start command and error handling
@raffleCmd.command(name='start')
async def raffleStart(context, name):
    if(contains(name, context.guild.id)==False):
        embed=discord.Embed(title="ERROR!", description="This raffle does not exist!",
        color=discord.Color.red())
        await context.send(embed=embed)
    else:
        temp = find(name, context.guild.id)
        message = await (temp.channel).fetch_message(temp.message)
        await message.remove_reaction('\U0001f60e', bot.user)
    if(context.author.name != find(name, context.guild.id).author):
        await message.add_reaction('\U0001f60e')
        embed=discord.Embed(title="ERROR!", description="You are not the creator of this raffle and cannot start it",
        color=discord.Color.red())
        await context.send(embed=embed)
    else:
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

# Raffle disband command and error handling
@raffleCmd.command(name='disband')
async def raffleDisband(context, name):
    if(contains(name, context.guild.id)==False):
        embed=discord.Embed(title="ERROR!", description="This raffle does not exist!",
        color=discord.Color.red())
        await context.send(embed=embed)
    elif((context.author.name != find(name, context.guild.id).author) and (context.author.guild_permissions.administrator == False)):
        embed=discord.Embed(title="ERROR!", description="You are not the creator of this raffle nor are you an admin and cannot disband it.",
        color=discord.Color.red())
        await context.send(embed=embed)
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

bot.run(TOKEN)

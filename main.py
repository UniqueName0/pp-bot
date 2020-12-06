import os
import discord
from discord.ext import commands
import random


token = os.getenv('token')

helptext = open('help.txt', 'r').read()

description= 'discord bot'

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='pp', description=description, intents=intents)

bot.remove_command('help')

flip = ['heads' , 'tails']
repeatlimit = 25
stopped = 0

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)

@bot.command()
async def help(ctx):
    await ctx.send(helptext)
    
@bot.command()
async def flip(ctx):
  flip = ['heads','tails']
  await ctx.send(random.choice(flip))

@bot.command()
async def repeat(ctx, times: int, content='repeating...'):
    global repeatlimit
    global stopped
    stopped = 0
    if times <= int(repeatlimit):
      for i in range(times):
        await ctx.send(content)
        if stopped == 1:
          break
    else:
      await ctx.send('you cannot repeat over {0} times'.format(repeatlimit))
      
@bot.command()
@commands.is_owner()
async def changerepeatlimit(ctx,arg):
  global repeatlimit
  repeatlimit = arg
  await ctx.send('the repeat limit is now {0}'.format(repeatlimit))
  
@bot.command()
async def stop(ctx):
  global stopped
  stopped = 1
  
bot.run(token)

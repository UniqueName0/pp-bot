import os
import discord
from discord.ext import commands
import random
import json

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
  
@bot.command()
async def bal(ctx):
  await open_account(ctx.author)
  user = ctx.author
  users = await get_bank_data()
  
  wallet_amt = users[str(user.id)]["wallet"]
  
  em = discord.Embed(title = f"{ctx.author.name}'s balance", color = discord.Color.red())
  em.add_field(name = "pp points", value = wallet_amt)
  await ctx.send(embed = em)
  
@bot.command()
async def work(ctx):
  await open_account(ctx.author)
  
  users = await get_bank_data()
  user = ctx.author
  earnings = random.randrange(101)
  
  await ctx.send(f"you got {earnings} pp points")
  
  users[str(user.id)]["wallet"] += earnings
  
  with open("mainbank.json", "w") as f:
    json.dump(users, f)
  
  
async def open_account(user):
  users = await get_bank_data()
  if str(user.id) in users:
    return False
  else:
    users[str(user.id)] = {}
    users[str(user.id)]["wallet"] = 0
    
  with open("mainbank.json", "w") as f:
    json.dump(users,f)
  return True
  
  
async def get_bank_data():
  with open("mainbank.json", "r") as f:
    users = json.load(f)
    
  return users
    
  
  
bot.run(token)

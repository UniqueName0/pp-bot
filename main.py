import os
import discord
from discord.ext import commands, tasks
from discord.ext.tasks import loop
import random
import json
import datetime

token = os.getenv('token')

helptext = open('help.txt', 'r').read()

description= 'discord bot'

intents = discord.Intents.default()
intents.members = True

global pre
pre = "pp"
bot = commands.Bot(command_prefix=pre, description=description, intents=intents)

bot.remove_command('help')

flip = ['heads' , 'tails']
repeatlimit = 25
stopped = 0

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    global users
    users = get_bank_data()

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
async def upgrade(ctx, arg):
  await open_account(ctx.author)
  user = ctx.author
  users = await get_bank_data()
  wallet_amt = users[str(user.id)]["wallet"]
  hourly_up_price = users[str(user.id)]["hourly"]*3
  payout_up_price = users[str(user.id)]["max_up"]*10
  if arg == "daily" and wallet_amt > hourly_up_price:
    users[str(user.id)]["hourly"] = users[str(user.id)]["hourly"]*2+100
    users[str(user.id)]["wallet"] -= hourly_up_price
    await ctx.send("daily earnings upgraded")
  elif arg == "payout" and wallet_amt > payout_up_price:
    users[str(user.id)]["max_up"] += 1
    users[str(user.id)]["wallet"] -= payout_up_price
    await ctx.send("max payout upgraded")
  else:
    await ctx.send("enter either daily or payout after ppupgrade, and make sure you can afford the upgrade")
  with open("mainbank.json","w") as f:
    json.dump(users,f)

@bot.command()
@commands.cooldown(1 ,120, commands.BucketType.user)
async def work(ctx):
  await open_account(ctx.author)
  
  users = await get_bank_data()
  user = ctx.author
  earnings = random.randrange(0, 100*users[str(user.id)]["max_up"])
  payout_up_price = users[str(user.id)]["max_up"]*150
  hourly_up_price = users[str(user.id)]["hourly"]*3
  
  em = discord.Embed(title = f"you got {earnings} pp points", color = discord.Color.red())
  em.add_field(name = f"max payout - upgrade cost: {payout_up_price}",value = users[str(user.id)]["max_up"]*100)
  em.add_field(name = f"daily - use ppcollect to collect - upgrade cost: {hourly_up_price}",value = users[str(user.id)]["hourly"])
  em.add_field(name = "upgrading", value = 'use "ppupgrade (payout or daily)" to upgrade this')
  await ctx.send(embed = em)
  
  users[str(user.id)]["wallet"] += earnings
  with open("mainbank.json","w") as f:
    json.dump(users,f)
  
@bot.command()
@commands.cooldown(1,86400, commands.BucketType.user)
async def collect(ctx):
  await open_account(ctx.author)
  user = ctx.author
  users = await get_bank_data()
  users[str(user.id)]["wallet"] += users[str(user.id)]["hourly"]
  z = users[str(user.id)]["hourly"]
  await ctx.send(f"you got {z} pp points")
  with open("mainbank.json","w") as f:
    json.dump(users,f)

@bot.command()
@commands.is_owner()
async def prefix(ctx, arg):
  global pre
  pre = arg
  bot.command_prefix = pre
    
@work.error
async def work_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = 'This command is on cooldown {:.1f}s'.format(error.retry_after)
        await ctx.send(msg)
    else:
        raise error
  
async def open_account(user):
  users = await get_bank_data()
  if str(user.id) in users:
    return False
  else:
    users[str(user.id)] = {}
    users[str(user.id)]["wallet"] = 0
    users[str(user.id)]["max_up"] = 1
    users[str(user.id)]["hourly"] = 100
    
  with open("mainbank.json", "w") as f:
    json.dump(users,f)
  return True
  
  
async def get_bank_data():
  with open("mainbank.json", "r") as f:
    users = json.load(f)
    
  return users
    
  
bot.run(token)

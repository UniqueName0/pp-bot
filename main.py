import os
import discord
import discord.utils
from discord.ext import commands, tasks
from discord.ext.tasks import loop
from discord.utils import get
import random
import json
import datetime
from discord import Permissions

token = os.getenv('token')

helptext = open('help.txt', 'r').read()

description= 'discord bot'

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="pp", description=description, intents=intents)

bot.remove_command('help')

flip = ['heads' , 'tails']
stopped = 0
re = 2500000000000000000000000000000000

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
@commands.is_owner()
async def ban (ctx, member:discord.User=None, reason =None):
    if member == None or member == ctx.message.author:
        await ctx.channel.send("You cannot ban yourself")
        return
    if reason == None:
        reason = "being a penis"
    message = f"You have been banned from {ctx.guild.name} for {reason}"
    await member.send(message)
    await ctx.guild.ban(member, reason=reason)
    await ctx.channel.send(f"{member} is banned!")

@bot.command()
async def repeat(ctx, times: int, content='repeating...'):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()
    global stopped
    stopped = 0
    if str(ctx.message.guild.id) in users:
      pass
    else:
      users[str(ctx.message.guild.id)] = {}
      users[str(ctx.message.guild.id)]["repeatlimit"] = 25000000000000000000
      users[str(ctx.message.guild.id)]["check"] = 1
      with open("mainbank.json","w") as f:
        json.dump(users,f)
    re = users[str(ctx.message.guild.id)]["repeatlimit"]
    if times <= int(re):
      for i in range(times):
        await ctx.send(content)
        if stopped == 1:
          break
    else:
      await ctx.send('you cannot repeat over {0} times'.format(re))
      
@bot.command()
@commands.is_owner()
async def changerepeatlimit(ctx,arg):
  await open_account(ctx.author)
  user = ctx.author
  users = await get_bank_data()
  if str(ctx.message.guild.id) in users:
    pass
  else:
    users[str(ctx.message.guild.id)] = {}
    users[str(ctx.message.guild.id)]["repeatlimit"] = 2500000000000000000
    users[str(ctx.message.guild.id)]["check"] = 1
    with open("mainbank.json","w") as f:
      json.dump(users,f)
  users = await get_bank_data()
  users[str(ctx.message.guild.id)]["repeatlimit"] = arg
  with open("mainbank.json","w") as f:
    json.dump(users,f)
  users = await get_bank_data()
  re = users[str(ctx.message.guild.id)]["repeatlimit"]
  await ctx.send('the repeat limit is now {0}'.format(re))
  with open("mainbank.json","w") as f:
    json.dump(users,f)

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
  bot.command_prefix = arg
    
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

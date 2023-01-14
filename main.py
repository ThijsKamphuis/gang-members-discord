import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json
import random

# .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_ID')
INTENTS = discord.Intents.all()

# searchgame
searchinggame = 882251818569195540
bottest = 882574276765564989
queue = []
queuesize = 0
queuestarted = False

role_csgo = 1053745890613010442

def startqueue():
    global queuestarted
    queuestarted = True

def endqueue():
    global queuestarted, queue
    queuestarted = False



bot = discord.Bot()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# 727
@bot.slash_command(name="727", guild_ids=[GUILD], description='727?')
async def gif727(ctx):
    await ctx.respond(random.sample(json.load(open('gifs.json')), 1)[0])
    return    

# gm quote random
@bot.slash_command(name="gmquote", guild_ids=[GUILD], description='Random Gang Member Quote')
async def gmquote(ctx):
    gm_quote = random.sample(json.load(open('quotes.json')), 1)[0]
    await ctx.respond(f'> {gm_quote["Quote"]}\n**~{gm_quote["Author"]}, {gm_quote["Year"]}**')



# gm quote add
@bot.slash_command(name="gmquoteadd", guild_ids=[GUILD], description='Add a Gang Member Quote')
async def gmquote(ctx: discord.ApplicationContext, quote: str, author: str, year: int):
    
    quotelist = json.load(open('quotes.json'))
    quotelist.append({"Quote":quote,"Author":author,"Year":year})    
    with open('quotes.json', 'w') as outfile:
        json.dump(quotelist, outfile)
        
    await ctx.respond(f'> {quote}\n**~{author}, {year}**\n Quote successfully added!')


bot.run(TOKEN)

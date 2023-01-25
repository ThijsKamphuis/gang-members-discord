import discord
from discord.ext import commands
from discord.utils import get_or_fetch
import os
from dotenv import load_dotenv
import json
import random
from datetime import datetime
from dateutil import relativedelta
import requests

# .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_ID')
INTENTS = discord.Intents.all()

gm_guild_id = 882248303822123018

bot = discord.Bot(intents=INTENTS)


motm_channel_id = 1065028419487793182
motm_role_id = 1062507887718567986

GMDev_id = 1059968168493318198
GMAdmin_id = 882248427298230292



# GIFS
tenor_api_key = "AIzaSyCLBIeUiywmo5JIwqImRcRnUMjxwYtXptk"
client_key = "gang_members_bot"
search_limit = 50


def get_motm() -> discord.Member:
    motm = bot.get_guild(gm_guild_id).get_role(motm_role_id).members[0]
    return motm

def votingdaysleft():
    voting_days_left = (abs(datetime.today() - ((datetime.today() + (relativedelta.relativedelta(months=1))).replace(day=1, hour= 0, minute= 0, second=1, microsecond= 0)))).days
    return voting_days_left



@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="polish moments"))


# 727
@bot.slash_command(name="727", description='727?')
async def gif727(ctx):
    r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % ("727", tenor_api_key, client_key,  search_limit))

    if r.status_code == 200:
        gifs = json.loads(r.content)
        await ctx.respond(random.sample(gifs, 1))
    else:
        await ctx.respond(r.status_code)


    return    

# JORN GIF
@bot.slash_command(name="vallas", description='JORN (VALLAS)')
async def jorngif(ctx):
    await ctx.respond("https://tenor.com/view/jorn-discord-mod-letterlijk-jorn-gif-27345172")
    return    

##### QUOTES #####

# gm quote random
@bot.slash_command(name="gmquote", description='Random Gang Member Quote')
async def gmquote(ctx):
    gm_quote = random.sample(json.load(open('quotes.json')), 1)[0]
    await ctx.respond(f'> {gm_quote["Quote"]}\n**~{gm_quote["Author"]}, {gm_quote["Year"]}**')

# gm quote add
@bot.slash_command(name="gmquoteadd", description='Add a Gang Member Quote')
async def gmquoteadd(ctx: discord.ApplicationContext, quote: str, author: str, year: int):
    
    quotelist = json.load(open('quotes.json'))
    quotelist.append({"Quote":quote,"Author":author,"Year":year})    
    with open('quotes.json', 'w') as outfile:
        json.dump(quotelist, outfile, indent=4)

    await ctx.respond(f'> {quote}\n**~{author}, {year}**\n Quote successfully added!')


##### MOTM #####

# INIT
@bot.slash_command(name="motminit", description="Initialize MOTM (ADMIN ONLY)")
@commands.has_any_role(GMDev_id, GMAdmin_id)
async def motminit(ctx):
    await ctx.respond("Initializing MOTM")

    motm = get_motm()

    

    global embed
    embed = discord.Embed(
        title="Member of the Month",
        color=0xffffff
    )

    embed.add_field(
        name="Current MotM:",
        value=f"<@{motm.id}>",
        inline=True
    )

    embed.add_field(
        name="Days left to vote:",
        value=str(votingdaysleft()),
        inline=True
    )

    users = ["user1", "user2", "user3"]

    standings_list = "\n".join([f"{i}. {user}: 5" for i, user in enumerate(users, start=1)])

    embed.add_field(
        name="Current Standings",
        value=standings_list,
        inline=False
    )

    embed.set_footer(text="Use /motmvote @user to vote!")
    global ch
    ch = bot.get_channel(motm_channel_id)
    await ch.purge()

    await ch.send(embed=embed)


@bot.slash_command(name="motmvote", description="Vote for MOTM")    
async def vote(ctx: discord.ApplicationContext, member: discord.Member):
    return
    



# Check for new day
if not datetime.today().hour:
    async def update_embed():

        votingdaysleft()
        global ch
        await ch.purge()
        await ch.send(embed=embed)



bot.run(TOKEN)

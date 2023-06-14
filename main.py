from unicodedata import name
import discord
from discord.ext import commands
import discord.utils
import os
from dotenv import load_dotenv
from num2words import num2words
import requests
import json


#### SETUP ####
load_dotenv()

#### BOT INIT ####
class GangMemberBot(discord.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        
        super().__init__(intents=intents)
    
bot = GangMemberBot()

#### IDS ####
gm_guild_id = 882248303822123018

motm_channel_id = 1065028419487793182
motm_role_id = 1062507887718567986

GMDev_id = 1059968168493318198
GMStaff_id = 1067195296993517568
GMAdmin_id = 882248427298230292
GM_id = 882248832354750524

#### STARTUP ####
@bot.event
async def on_connect():
    bot.load_extension("cogs.gifs")
    bot.load_extension("cogs.quote")
    bot.load_extension("cogs.motm")
    bot.load_extension("cogs.activity")
    bot.load_extension("cogs.birthday")
    await bot.sync_commands()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    
    #await bot.get_guild(gm_guild_id).get_member(1059183824749199380).edit(nick=None)


#### ON MEMBER JOIN ####
@bot.event
async def on_member_join(member):
    await member.add_roles(bot.get_guild(gm_guild_id).get_role(882251536653230151))
    member_count = bot.get_guild(gm_guild_id).member_count
    count_suffix = num2words(member_count, to='ordinal')[-2:]
    if (member_count % 100) == 0:
        await bot.get_channel(882248303822123021).send(f"Congratulations <@{member.id}>, welcome to Gang Members. You are the {member_count}{count_suffix} member to join!!!!!!")
    else:
        await bot.get_channel(882248303822123021).send(f"Hello <@{member.id}>, welcome to Gang Members. You are the {member_count}{count_suffix} member to join.")

@bot.event
async def on_member_remove(member):    
    birthdaysdb = json.load(open('databases/birthdays.json', encoding="utf-8"))
    if str(member.id) in birthdaysdb.keys():
        birthdaysdb.pop(str(member.id))
    
    motmvotesdb = json.load(open('databases/motm_votes.json', encoding="utf-8"))
    for vote in motmvotesdb:
        if str(member.id) in vote["Vote"] or str(member.id) in vote["User"]:
            motmvotesdb.remove(vote)
        
    with open('databases/birthdays.json', 'w') as outfile:
        json.dump(birthdaysdb, outfile, indent=4)
    with open('databases/motm_votes.json', 'w') as outfile:
        json.dump(motmvotesdb, outfile, indent=4)

async def download_pfps():
    for member in (bot.get_guild(gm_guild_id).members):
        print(member)
        open(f"profilepics/{member.name}.png", "wb").write(requests.get(member.display_avatar.url, allow_redirects=True).content)
                
bot.run(os.getenv('DISCORD_TOKEN'))

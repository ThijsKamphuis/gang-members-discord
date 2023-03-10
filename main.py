from unicodedata import name
import discord
from discord.ext import commands
import discord.utils
import os
from dotenv import load_dotenv
from num2words import num2words
import requests


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
    bot.load_extension("cogs.noterix")
    bot.load_extension("cogs.gifs")
    bot.load_extension("cogs.quote")
    bot.load_extension("cogs.motm")
    bot.load_extension("cogs.roles")
    bot.load_extension("cogs.activity")
    bot.load_extension("cogs.birthday")
    await bot.sync_commands()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


#### ON MEMBER JOIN ####
@bot.event
async def on_member_join(member):
    await member.add_roles(bot.get_guild(gm_guild_id).get_role(882251536653230151))
    
    member_count = bot.get_guild(gm_guild_id).member_count
    count_suffix = num2words(member_count, to='ordinal')[-2:]
    await bot.get_channel(882248303822123021).send(f"Hello <@{member.id}>, welcome to Gang Members. You are the {member_count}{count_suffix} member to join.")

#### DOWNLOAD ####
@bot.slash_command(name="downloadpfps", description="download pfp of every member (STAFF ONLY)")
@commands.has_any_role(GMStaff_id, GMAdmin_id)
async def download_pfps(ctx):
    for member in (bot.get_guild(gm_guild_id).members):
        print(member)
        open(f"profilepics/{member.name}.png", "wb").write(requests.get(member.display_avatar.url, allow_redirects=True).content)
                
@download_pfps.error
async def motmvote_role_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.respond("You do not have permission to use this command. (STAFF ONLY)", ephemeral=True)
    else:
        raise error
    
bot.run(os.getenv('DISCORD_TOKEN'))

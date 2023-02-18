from cgitb import reset
from ssl import cert_time_to_seconds
from time import time, timezone
import discord
from discord.ext import commands
from discord.ext import tasks
import discord.utils
import os
from dotenv import load_dotenv
import json
import random
from datetime import datetime, timezone, tzinfo
from dateutil import relativedelta
import math
from collections import defaultdict
from re import sub
import asyncio
from num2words import num2words

##### .env ####
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_ID')
INTENTS = discord.Intents.all()

gm_guild_id = 882248303822123018

bot = discord.Bot(intents=INTENTS)


motm_channel_id = 1065028419487793182
motm_role_id = 1062507887718567986

GMDev_id = 1059968168493318198
GMStaff_id = 1067195296993517568
GMAdmin_id = 882248427298230292
GM_id = 882248832354750524


def get_motm() -> discord.Member:
    motm = bot.get_guild(gm_guild_id).get_role(motm_role_id).members[0]
    return motm


def votingdaysleft():
    voting_days_left = (abs(datetime.today() - ((datetime.today() + (relativedelta.relativedelta(months=1))).replace(day=1, hour= 0, minute= 0, second=1, microsecond= 0)))).days
    return voting_days_left


##### STARTUP #####
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="polish moments"))
    refresh_MOTM.start()
    check_for_month.start()
    
##### 727 #####
@bot.slash_command(name="727", description='727?')
async def gif727(ctx):

    await ctx.respond(random.sample(json.load(open('databases/gifs.json', encoding="utf-8")), 1)[0])
    return    

##### JORN GIF #####
@bot.slash_command(name="vallas", description='JORN (VALLAS)')
async def jorngif(ctx):
    await ctx.respond("https://tenor.com/view/jorn-discord-mod-letterlijk-jorn-gif-27345172")
    return    

##### MANOE GIF #####
@bot.slash_command(name="manoe", description='MANOE')
async def manoegif(ctx):
    await ctx.respond("https://tenor.com/view/manoe-gangmembers-gm-gif-27494707")
    return  



##### QUOTES #####
def get_quote_page(page):
    quote_list = json.load(open('databases/quotes.json', encoding="utf-8"))

    totalpages = (math.ceil(len(quote_list) / 6))
    quoteindex = 0 + ((page - 1) * 6)

    global current_page, total_pages
    current_page = page
    total_pages = totalpages



    global quote_embed
    if page < totalpages:
        quote_embed = discord.Embed(
            title=f"Gang Member Quotes \t Page {page} / {totalpages}",
            color=0xae8cff
        )
        quote_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/914862282335453215/1067193702038110228/favicon.png")

        for x in range(quoteindex, (quoteindex + 6)):
            quote_embed.add_field(
                name=quote_list[quoteindex]["Quote"],
                value=f'{quote_list[quoteindex]["Author"]}, {quote_list[quoteindex]["Year"]}\n \u200B',
                inline=False
            )
            quoteindex += 1
    elif page == totalpages:
        quote_embed = discord.Embed(
            title=f"Gang Member Quotes \t Page {page} / {totalpages}",
            color=0xae8cff
        )
        quote_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/914862282335453215/1067193702038110228/favicon.png")

        for z in range(quoteindex, len(quote_list)):
            quote_embed.add_field(
                name=quote_list[quoteindex]["Quote"],
                value=f'{quote_list[quoteindex]["Author"]}, {quote_list[quoteindex]["Year"]}\n \u200B',
                inline=False
            )
            quoteindex += 1

# GM QUOTE RANDOM
@bot.slash_command(name="gmquote", description='Random Gang Member Quote')
async def gmquote(ctx):
    gm_quote = random.sample(json.load(open('databases/quotes.json', encoding="utf-8")), 1)[0]
    await ctx.respond(f'> {gm_quote["Quote"]}\n**~{gm_quote["Author"]}, {gm_quote["Year"]}**')


# GM QUOTE ADD
@bot.slash_command(name="gmquoteadd", description='Add a Gang Member Quote')
async def gmquoteadd(ctx: discord.ApplicationContext, quote: str, author: str, year: int):
    
    quotelist = json.load(open('databases/quotes.json', encoding="utf-8"))
    quotelist.append({"Quote":quote,"Author":author,"Year":year})    
    with open('databases/quotes.json', 'w') as outfile:
        json.dump(quotelist, outfile, indent=4)

    await ctx.respond(f'> {quote}\n**~{author}, {year}**\n Quote successfully added!')


# GM QUOTE LIST ALL

class QuoteButtonsView(discord.ui.View):
    @discord.ui.button(label="Prev", style=discord.ButtonStyle.primary, emoji="⬅")
    async def prev(self, button: discord.ui.Button, interaction: discord.Interaction):
        if current_page > 1:
            get_quote_page((current_page - 1))
            await interaction.response.edit_message(embed = quote_embed)
        else:
            await interaction.response.edit_message(embed = quote_embed)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, emoji="➡")
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        if current_page < total_pages:
            get_quote_page((current_page + 1))
            await interaction.response.edit_message(embed = quote_embed)
        else:
            await interaction.response.edit_message(embed = quote_embed)


@bot.slash_command(name="gmquotelist", description='List all Gang Member Quotes')
async def gmquotelist(ctx):

    get_quote_page(1)
    await ctx.respond(embed = quote_embed, view = QuoteButtonsView(), ephemeral=True)





##### MOTM #####

# Count votes
def count_votes():
    global vote_standings
    motm_votes_db = json.load(open('databases/motm_votes.json', encoding="utf-8"))
    vote_standings = defaultdict(int)
    for i in motm_votes_db:
        if i in motm_votes_db:
            vote_standings[i["Vote"]] += 1
        else:
            vote_standings[i["Vote"]] = 1
            
    vote_standings = sorted(vote_standings.items(), key=lambda item: item[1], reverse=True)
    return vote_standings
    

# Generate embed with most recent data
def motm_embed_gen():
    motm = get_motm()
    global motm_embed
    motm_embed = discord.Embed(
        title="Member of the Month",
        color=motm.color
    )

    motm_embed.set_thumbnail(url=motm.display_avatar.url)
    
    motm_embed.add_field(
        name="Current MotM:",
        value=f"<@{motm.id}>",
        inline=True
    )

    motm_embed.add_field(
        name="Days left to vote:",
        value=str(votingdaysleft()),
        inline=True
    )
    count_votes()
    
    standings_list = "\n".join([f"{i}. <@{user[0]}>: **{user[1]}**" for i, user in enumerate(vote_standings, start=1)])
    

    motm_embed.add_field(
        name="Standings:",
        value=standings_list,
        inline=False
    )

    motm_embed.set_footer(text="Use /motmvote @user to vote!")

async def edit_embed():
    
    # Generate embed
    motm_embed_gen()
    
    # Fetch message ID
    motm_db = json.load(open('databases/motm.json', encoding="utf-8"))
    motm_db_ID = motm_db[0]["MOTM_Message_ID"]
    
    # Edit message
    ch = bot.get_channel(motm_channel_id)  
    msg = await ch.fetch_message(motm_db_ID)
    await msg.edit(embed= motm_embed)
    return

# INIT
@bot.slash_command(name="motminit", description="Initialize MOTM (STAFF ONLY)")
@commands.has_any_role(GMDev_id, GMAdmin_id, GMStaff_id)
async def motminit(ctx):
    await ctx.respond("Initializing MOTM", ephemeral=True)
    motm_embed_gen() 

    ch = bot.get_channel(motm_channel_id)
    await ch.purge()
    motm_message = await ch.send(embed= motm_embed)
    
    motm_db = json.load(open('databases/motm.json', encoding="utf-8"))
    motm_db[0]["MOTM_Message_ID"] = motm_message.id
    with open('databases/motm.json', 'w') as outfile:
        json.dump(motm_db, outfile, indent=4)
    

@motminit.error
async def motminit_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.respond("You do not have permission to use this command. (STAFF ONLY)", ephemeral=True)
    else:
        raise error

# Delete embed
@bot.slash_command(name="motmdel", description="Purge MOTM channel (DEV ONLY)")
@commands.has_any_role(GMDev_id)
async def motmdel(ctx):

    ch = bot.get_channel(motm_channel_id)

    await ctx.respond("Purging", ephemeral=True)
    await ch.purge()
    
    motm_db = json.load(open('databases/motm.json', encoding="utf-8"))
    motm_db[0]["MOTM_Message_ID"] = "0"
    with open('databases/motm.json', 'w') as outfile:
        json.dump(motm_db, outfile, indent=4)


@tasks.loop(hours=1.0)
async def refresh_MOTM():
    await edit_embed()
 
# Vote  
@bot.slash_command(name="motmvote", description="Vote for MOTM (GM ONLY)")
@commands.has_any_role(GM_id)
async def motmvote(ctx: discord.ApplicationContext, user: str):
    voter = sub("[<,>,@]", "", str(ctx.author.id))
    user = sub("[<,>,@]", "", str(user))
    
    GM_role = discord.utils.get(ctx.guild.roles, id=GM_id)
    GMadmin_role = discord.utils.get(ctx.guild.roles, id=GMAdmin_id)
    user_model = bot.get_guild(gm_guild_id).get_member(int(user))
    
    if (GM_role in user_model.roles):
        if (GMadmin_role in user_model.roles):
            await ctx.respond("Chosen user is an Admin", ephemeral=True)
        else:
            motm_votes_db = json.load(open('databases/motm_votes.json', encoding="utf-8"))
            if not any(d["User"] == voter for d in motm_votes_db):
                motm_votes_db.append({"Vote":user,"User":voter})
                with open('databases/motm_votes.json', 'w') as outfile:
                    json.dump(motm_votes_db, outfile, indent=4)

                await ctx.respond(f"You voted for <@{user}>.", ephemeral=True)
            else:
                await ctx.respond("You already voted", ephemeral=True)

    else:
        await ctx.respond("Chosen user is not a GangMember", ephemeral=True)
    
    await refresh_MOTM()
    
@motmvote.error
async def motmvote_role_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.respond("You do not have permission to use this command. (GM ONLY)", ephemeral=True)
    else:
        raise error   
  
@motmvote.error   
async def motm_value_error(ctx: discord.ApplicationContext, error: discord.errors.ApplicationCommandInvokeError):
    if isinstance(error, discord.errors.ApplicationCommandInvokeError):
        await ctx.respond("Invalid input, mention a user", ephemeral=True)


# Results
def reset_voting():
    # Generate archive name (prev month)
    archive_file_name = f"votes_{(datetime.now().month) - 1}_{datetime.now().year}"
    
    # Copy votes to archive
    open(f"archive/{archive_file_name}.json", "w").write(open("databases/motm_votes.json").read())
    
    # Empty votes
    with open('databases/motm_votes.json', 'w') as outfile:
        json.dump([], outfile, indent=4)
    

def edit_motm():
    #remove motm role from current motm
    #give role to next motm
    print()
    

@tasks.loop(minutes=1)
async def check_for_month():
    if datetime.now().day == 1:
        reset_voting()
        edit_motm()
        asyncio.run(refresh_MOTM())
    
# JOIN MESSAGE
channel_new = 882248303822123021
@bot.event
async def on_member_join(member):
    member_count = bot.get_guild(gm_guild_id).member_count
    count_suffix = num2words(member_count, to='ordinal')[-2:]
    await bot.get_channel(channel_new).send(f"Hello @{member}, welcome to Gang Members. You are the {member_count}{count_suffix} member to join.")




bot.run(TOKEN)

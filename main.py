import discord
from discord.ext import commands
from discord.ext import pages
from discord.utils import get_or_fetch
import os
from dotenv import load_dotenv
import json
import random
from datetime import datetime
from dateutil import relativedelta
import math
import asyncio

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

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, emoji="➡")
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        if current_page < total_pages:
            get_quote_page((current_page + 1))

            await interaction.response.edit_message(embed = quote_embed)





@bot.slash_command(name="gmquotelist", description='List all Gang Member Quotes (STAFF ONLY)')
@commands.has_any_role(GMDev_id, GMAdmin_id, GMStaff_id)
async def gmquotelist(ctx):

    get_quote_page(1)
    await ctx.respond(embed = quote_embed, view = QuoteButtonsView(), ephemeral=True)



    
    #get_quote_page(1)
    #await ctx.interaction.response.send_message(embed=quote_embed, ephemeral=True)

    #get_quote_page(2)
    #await ctx.interaction.edit_original_response(embed=quote_embed)

            












@gmquotelist.error
async def gmquote_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.respond("You do not have permission to use this command. (STAFF ONLY)", ephemeral=True)
    else:
        raise error



##### MOTM #####

# INIT
@bot.slash_command(name="motminit", description="Initialize MOTM (STAFF ONLY)")
@commands.has_any_role(GMDev_id, GMAdmin_id, GMStaff_id)
async def motminit(ctx):
    await ctx.respond("Initializing MOTM")

    motm = get_motm()


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

    #users = ["user1", "user2", "user3"]

    #standings_list = "\n".join([f"{i}. {user}: 5" for i, user in enumerate(users, start=1)])

    #embed.add_field(
        #name="Current Standings",
        #value=standings_list,
        #inline=False
    #)

    embed.set_footer(text="Use /motmvote @user to vote!")

    ch = bot.get_channel(motm_channel_id)
    await ch.purge()

    await ch.send(embed=embed)

@motminit.error
async def motminit_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.respond("You do not have permission to use this command. (STAFF ONLY)", ephemeral=True)
    else:
        raise error
    




bot.run(TOKEN)

from turtle import width
import discord
from discord.ext import commands
from discord.ext import tasks
import discord.utils
import os
from dotenv import load_dotenv
import json
import random
from datetime import datetime, date, timedelta
from dateutil import relativedelta
import math
from collections import defaultdict
from re import sub
from num2words import num2words
import mysql.connector

#### SETUP ###################################################
load_dotenv()

#### SQL ####



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

#### STARTUP ###################################################
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="polish moments"))
    refresh_MOTM.start()
    check_for_month.start()
    bot.add_view(GameRoleSelectMenu())
    
    
    
#### GIF COMMANDS ###################################################  
#### 727 GIF ####
@bot.slash_command(name="727", description='727?')
async def gif727(ctx):

    await ctx.respond(random.sample(json.load(open('databases/gifs.json', encoding="utf-8")), 1)[0])
    return    

#### JORN GIF ####
@bot.slash_command(name="vallas", description='JORN (VALLAS)')
async def jorngif(ctx):
    await ctx.respond("https://tenor.com/view/jorn-discord-mod-letterlijk-jorn-gif-27345172")
    return    

#### MANOE GIF ####
@bot.slash_command(name="manoe", description='MANOE')
async def manoegif(ctx):
    await ctx.respond("https://tenor.com/view/manoe-gangmembers-gm-gif-27494707")
    return  



##### QUOTES ###################################################
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

#### QUOTE RANDOM ####
@bot.slash_command(name="gmquote", description='Random Gang Member Quote')
async def gmquote(ctx):
    gm_quote = random.sample(json.load(open('databases/quotes.json', encoding="utf-8")), 1)[0]
    await ctx.respond(f'> {gm_quote["Quote"]}\n**~{gm_quote["Author"]}, {gm_quote["Year"]}**')


#### QUOTE ADD ####
@bot.slash_command(name="gmquoteadd", description='Add a Gang Member Quote')
async def gmquoteadd(ctx: discord.ApplicationContext, quote: str, author: str, year: int):     
    quotelist = json.load(open('databases/quotes.json', encoding="utf-8"))
    quotelist.append({"Quote":quote,"Author":author,"Year":year})
    with open('databases/quotes.json', 'w') as outfile:
        json.dump(quotelist, outfile, indent=4)

    await ctx.respond(f'> {quote}\n**~{author}, {year}**\n Quote successfully added!')

#### QUOTE LIST ####
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


##### MOTM ###################################################

def get_motm() -> discord.Member:
    motm = bot.get_guild(gm_guild_id).get_role(motm_role_id).members[0]
    return motm

def votingdaysleft():
    voting_days_left = (abs(datetime.today() - ((datetime.today() + (relativedelta.relativedelta(months=1))).replace(day=1, hour= 0, minute= 0, second=1, microsecond= 0)))).days
    return voting_days_left


#### COUNT VOTES ####
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
    

#### GENERATE EMBED ####
def motm_embed_gen():
    motm = get_motm()
    global motm_embed
    motm_embed = discord.Embed(
        title="Member of the Month",
        color=motm.color
    )

    motm_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/914862282335453215/1067193702038110228/favicon.png")
    motm_embed.set_image(url=motm.display_avatar.url)
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

    motm_embed.set_footer(text="Use /motmvote @user to vote!")

#### EDIT EMBED ####
async def edit_embed():
    motm_embed_gen()
    
    motm_db = json.load(open('databases/motm.json', encoding="utf-8"))
    motm_db_ID = motm_db[0]["MOTM_Message_ID"]
    
    ch = bot.get_channel(motm_channel_id)  
    msg = await ch.fetch_message(motm_db_ID)
    await msg.edit(embed= motm_embed)
    return

#### INIT MOTM ####
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

#### DEL EMBED ####
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
 
#### VOTE MOTM ####
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


#### MOTM STANDINGS ####
@bot.slash_command(name="motmstandings", description="View MOTM standings (ADMIN ONLY)")
@commands.has_any_role(GMAdmin_id)
async def motmstandings(ctx):
    await ctx.respond("\n".join([f"{i}. <@{user[0]}>: **{user[1]}**" for i, user in enumerate(count_votes(), start=1)]), ephemeral = True)
    
@motmstandings.error
async def motmstandings_role_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.respond("You do not have permission to use this command. (ADMIN ONLY)", ephemeral=True)
    else:
        raise error     
    
#### RESET VOTES ####
def reset_voting():

    archive_file_name = f"votes_{datetime.now().month}_{datetime.now().year}"
    
    open(f"archive/{archive_file_name}.json", "w").write(open("databases/motm_votes.json").read())
    
    with open('databases/motm_votes.json', 'w') as outfile:
        json.dump([], outfile, indent=4)
        
#### ANNOUNCE MOTM ####       
async def motm_announce():
    motm = get_motm()
    
    
    standings_list = "\n".join([f"{i}. <@{user[0]}>: **{user[1]}**" for i, user in enumerate(vote_standings, start=1)])
    
    motm_announce_embed = discord.Embed(
        title="New Member of the Month",
        color=motm.color
    )

    motm_announce_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/914862282335453215/1067193702038110228/favicon.png")
    motm_announce_embed.set_image(url=motm.display_avatar.url)
    
    motm_announce_embed.add_field(
        name=f"Our new Member of the month is {motm.display_name}!",
        value=f"<@{motm.id}> won with {vote_standings[0][1]} votes.",
        inline=False
    )
    

    motm_announce_embed.add_field(
    name="Results:",
    value=standings_list,
    inline=False
    )
    
    await bot.get_channel(882252560608657408).send(embed= motm_announce_embed)
    
#### EDIT MOTM ROLE ####
async def edit_motm_role():
    motm = get_motm()
    motm_role = bot.get_guild(gm_guild_id).get_role(motm_role_id)
    
    await motm.remove_roles(motm_role)
    await bot.get_guild(gm_guild_id).get_member(int(vote_standings[0][0])).add_roles(motm_role)
  

#### CHECK FOR NEW MONTH ####
@tasks.loop(minutes=1)
async def check_for_month():

    motm_month = (date.today().month)
    first_of_month = datetime(date.today().year, motm_month, 1, hour=0, minute=1)
    
    if (first_of_month <= datetime.now() <= (first_of_month + timedelta(minutes=1))):
        count_votes()
        if vote_standings[0][1] == vote_standings[1][1]:
            if random.randint(1,2) == 2:
                vote_standings[0],vote_standings[1] = vote_standings[1],vote_standings[0]
                
        await edit_motm_role()
        await motm_announce()
        reset_voting()
        await refresh_MOTM()
    
#### ON MEMBER JOIN ###################################################
@bot.event
async def on_member_join(member):
    await member.add_roles(bot.get_guild(gm_guild_id).get_role(882251536653230151))
    
    member_count = bot.get_guild(gm_guild_id).member_count
    count_suffix = num2words(member_count, to='ordinal')[-2:]
    await bot.get_channel(882248303822123021).send(f"Hello <@{member.id}>, welcome to Gang Members. You are the {member_count}{count_suffix} member to join.")



#### ROLES ###################################################
channel_game_roles = 1053743315696234496
# ROLES
game_roles = {
    "Counter Strike: Global Offensive":1053745890613010442,
    "ARK: Survival Evolved":1053745911987175544,
    "Grand Theft Auto V":1053745915426504735,
    "Minecraft":1053745896015274014,
    "Left 4 Dead 2":1067495011681312868,
    "Among Us":1067494997324206090,
    "Project Zomboid":1067494972137426974,
    "Genshin Impact":1068517552055140432,
    "Hearts of Iron IV":1078440119645782137,
}

# LOGOS
game_logos = {
    "logo_csgo":"<:CSGOLogo:1053745573641064448>",
    "logo_ark":"<:ARKlogo:1053745532197150880>",
    "logo_gtav":"<:GTAlogo:1053745557379764275>",
    "logo_mc":"<:MClogo:1053745505814974505>",
    "logo_l4d2":"<:l4d2logo:1067494842449531042>",
    "logo_amongus":"<:amonguslogo:1067494866281570394>",
    "logo_zomboid":"<:Zomboidlogo:1067494894723145788>",
    "logo_genshin":"<:genshinlogo:1078439499400478821>",
    "logo_hoi4":"<:Hoi4logo:1078439486553337906>",
}


GameRole_embed = discord.Embed(
    title="Select your games",
    color=11439359,
    description="Here you can select from which games you want to see the channels."
)
GameRole_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/914862282335453215/1067193702038110228/favicon.png")
 
 
class GameRoleSelectMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    GameRolesList = [
            discord.SelectOption(
                label = "Counter Strike: Global Offensive", 
                emoji = game_logos["logo_csgo"]
                ),           
            discord.SelectOption(
                label = "ARK: Survival Evolved",
                emoji = game_logos["logo_ark"]
                ),
            discord.SelectOption(
                label = "Grand Theft Auto V",
                emoji = game_logos["logo_gtav"]
                ),
            discord.SelectOption(
                label = "Minecraft",
                emoji = game_logos["logo_mc"]
                ),
            discord.SelectOption(
                label = "Left 4 Dead 2",
                emoji = game_logos["logo_l4d2"]
                ),
            discord.SelectOption(
                label = "Among Us",
                emoji = game_logos["logo_amongus"]
                ),
            discord.SelectOption(
                label = "Project Zomboid",
                emoji = game_logos["logo_zomboid"]
                ),
            discord.SelectOption(
                label = "Genshin Impact",
                emoji = game_logos["logo_genshin"]
                ),
            discord.SelectOption(
                label = "Hearts of Iron IV",
                emoji = game_logos["logo_hoi4"]
                ),
        ]
    
    @discord.ui.select(
        placeholder = "Select your games",
        min_values = 0,
        max_values= len(GameRolesList),
        options= GameRolesList,
        custom_id = "ui.select:gameselectmenu"  
    )
    async def SelectMenu_callback(self, select: discord.ui.Select, interaction: discord.Interaction):            
        await interaction.response.send_message("Your roles have been updated", ephemeral= True, delete_after= 5)
        roles_member = bot.get_guild(gm_guild_id).get_member(interaction.user.id)
        for key in game_roles:
            if key in select.values:
                await roles_member.add_roles(bot.get_guild(gm_guild_id).get_role(game_roles[key]))
            else:
                await roles_member.remove_roles(bot.get_guild(gm_guild_id).get_role(game_roles[key]))
   
   
   
   
      
@bot.slash_command(label="gamerolesinit",description="Initialize game roles (STAFF ONLY)")
@commands.has_any_role(GMDev_id, GMAdmin_id, GMStaff_id)
async def gamerolesinit(ctx):
    await ctx.respond("Initializing")
    await bot.get_channel(channel_game_roles).send(embed = GameRole_embed, view = GameRoleSelectMenu())



@gamerolesinit.error
async def gamerolesinit_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.respond("You do not have permission to use this command. (STAFF ONLY)", ephemeral=True)
    else:
        raise error



#### SEND MESSAGE AS BOT ###################################################
@bot.slash_command(label="sendmsg",description="(DEV ONLY)")
@commands.has_any_role(GMDev_id)
async def sendmsg(ctx: discord.ApplicationContext, channel: str, message: str):
    await ctx.respond("Sending", ephemeral = True)
    await bot.get_channel(int(channel)).send(message)

@sendmsg.error
async def sendmsg_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.respond("You do not have permission to use this command. (DEV ONLY)", ephemeral=True)
    else:
        raise error



#### EVENTS ###################################################
#### SEND EVENT BY ID ####
@bot.slash_command(label="sendevent", description="share an event from noterix.com")
@commands.has_any_role(GMStaff_id, GMAdmin_id)
async def sendevent(ctx: discord.ApplicationContext, eventid: str):
    
    event_db = mysql.connector.connect(
    host= os.getenv('SQL_HOST'),
    user= os.getenv('SQL_USER'),
    password= os.getenv('SQL_PASS'),
    database= os.getenv('SQL_DB')
    )
    event_db_cursor = event_db.cursor()
    
    event_db_cursor.execute(f"SELECT * FROM events WHERE id = '{eventid}'")
    event_details = (event_db_cursor.fetchall())[0]
    event_db.close()

    event_embed = discord.Embed(
        title = event_details[2],
        description = event_details[3].replace("<br />", "\n"),
        url=f"https://noterix.com/event?id={event_details[0]}",
        color=int("4540619")
    )
    event_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/914862282335453215/1067193702038110228/favicon.png")
    event_embed.set_image(url=event_details[9])
    event_embed.set_footer(text=f"https://noterix.com/event?id={event_details[0]}\nEvent hosted with Noterix.com")
    
    event_embed.add_field(
        name="Date",
        value=event_details[6],
        inline=True
    )
    event_embed.add_field(
        name="Time",
        value=event_details[7],
        inline=True
    )
    event_embed.add_field(
        name="Max visitors",
        value=event_details[8],
        inline=True
    )
    event_embed.add_field(
        name="Location",
        value=event_details[10],
        inline=False
    )  
    
    
    await ctx.respond(embed= event_embed)

        
@sendevent.error
async def sendevent_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.respond("You do not have permission to use this command. (STAFF ONLY)", ephemeral=True)
    else:
        raise error

#### ADD EVENT ####
@bot.slash_command(label="addevent", description="share an event from noterix.com")
@commands.has_any_role(GMStaff_id, GMAdmin_id)
async def addevent(ctx: discord.ApplicationContext, title: str, content: str, eventdate: str, eventtime: str, maxvisitors: int, location: str):
    event_db = mysql.connector.connect(
    host= os.getenv('SQL_HOST'),
    user= os.getenv('SQL_USER'),
    password= os.getenv('SQL_PASS'),
    database= os.getenv('SQL_DB')
    )
    event_db_cursor = event_db.cursor()
    
    event_id = random.randint(10000000000,99999999999)
    sql = "INSERT INTO events (id, owner, title, content, creationdate, creationtime, eventdate, eventtime, maxvisitors, photo, location, visibility) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (event_id, "65872", title, content, date.today().strftime("%d-%m-%Y"), datetime.now().strftime("%H:%M"), eventdate, eventtime, maxvisitors, "", location, "visible")
    event_db_cursor.execute(sql, val)
    event_db.commit()
    event_db.close()



    event_embed = discord.Embed(
        title = title,
        description = content,
        url=f"https://noterix.com/event?id={event_id}",
        color=int("4540619")
    )
    event_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/914862282335453215/1067193702038110228/favicon.png")
    event_embed.set_footer(text=f"https://noterix.com/event?id={event_id}\nEvent hosted with Noterix.com")
    
    event_embed.add_field(
        name="Date",
        value=eventdate,
        inline=True
    )
    event_embed.add_field(
        name="Time",
        value=eventtime,
        inline=True
    )
    event_embed.add_field(
        name="Max visitors",
        value=maxvisitors,
        inline=True
    )
    event_embed.add_field(
        name="Location",
        value=location,
        inline=False
    )  
    
    
    await ctx.respond(embed= event_embed)

        
@addevent.error
async def addevent_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.respond("You do not have permission to use this command. (STAFF ONLY)", ephemeral=True)
    else:
        raise error






bot.run(os.getenv('DISCORD_TOKEN'))

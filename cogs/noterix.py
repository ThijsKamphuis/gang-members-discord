import discord
from discord.ext import commands
import discord.utils
import os
from dotenv import load_dotenv
import random
from datetime import datetime, date
import mysql.connector
load_dotenv()

GMStaff_id = 1067195296993517568
GMAdmin_id = 882248427298230292

class noterix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    #### SEND EVENT BY ID ####
    @commands.slash_command(label="sendevent", description="share an event from noterix.com")
    @commands.has_any_role(GMStaff_id, GMAdmin_id)
    async def sendevent(self, ctx: discord.ApplicationContext, eventid: str):
        
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
        event_embed.set_footer(text=f"https://noterix.com/event?id={event_details[0]}\nPowered by Noterix.com")
        
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
    @commands.slash_command(label="addevent", description="share an event from noterix.com")
    @commands.has_any_role(GMStaff_id, GMAdmin_id)
    async def addevent(self, ctx: discord.ApplicationContext, title: str, content: str, eventdate: str, eventtime: str, maxvisitors: int, location: str):
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
        event_embed.set_footer(text=f"https://noterix.com/event?id={event_id}\nPowered by Noterix.com")
        
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





def setup(bot):
    bot.add_cog(noterix(bot))
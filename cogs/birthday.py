import discord
from discord.ext import commands
from discord.ext import tasks
import discord.utils
import json
from datetime import datetime, timedelta
import os
import mysql.connector


gm_guild_id = 882248303822123018

class birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.checkbirthday.start()
        
    @commands.slash_command(name="setbirthday", description="Add your birthday to the Gang Members calendar.")
    async def setbirthday(self, ctx: discord.ApplicationContext, day: int, month: int, year: int):
        
        if datetime.strptime(f"{day:02d}-{month:02d}-{year}", "%d-%m-%Y"):
            
            send_sql(f"UPDATE discord_users SET birthday='{year}-{month:02d}-{day:02d}' WHERE userid='{ctx.user.id}'")
            print(f"{ctx.user.name} birthday added: {year}-{month:02d}-{day:02d}")
            
            
            
            await ctx.respond(f"Set {day:02d}-{month:02d}-{year} as your birthday.", ephemeral=True)
        else:
            ctx.respond("Wrong format, dd-mm-yyyy")
            return
            

     
     
     
                

    @commands.slash_command(name="nextbirthdays", description="View upcoming birthdays.")
    async def nextbirthdays(self, ctx: discord.ApplicationContext):
        og_birthdaysdb = json.load(open('databases/birthdays.json', encoding="utf-8"))

        birthdays = {k: v[:-4] + str(datetime.now().year) for k, v in og_birthdaysdb.items()}
        birthdays = {k: (datetime.strptime(v, "%d-%m-%Y") - datetime.now()).days + 1 for k, v in birthdays.items()}


        for k, v in birthdays.items():
            if v < 0:
                birthdays[k] += 365


        days_birthdays = dict(sorted(birthdays.items(), key=lambda x: x[1]))
        sorted_birthdays = {k: og_birthdaysdb[k] for k, v in days_birthdays.items()}
        
        birthdays_embed = discord.Embed(
            title= "Upcoming birthdays",
            color=0xae8cff
        )
        birthdays_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/914862282335453215/1067193702038110228/favicon.png")
        
        for birthday in sorted_birthdays:
            birthdays_embed.add_field(
                name= f"{self.bot.get_guild(gm_guild_id).get_member(int(birthday)).name} {f'({self.bot.get_guild(gm_guild_id).get_member(int(birthday)).nick})' if self.bot.get_guild(gm_guild_id).get_member(int(birthday)).nick else ''}",
                value=f"""Turns {datetime.now().year - datetime.strptime(sorted_birthdays[birthday][-4:], '%Y').year if datetime.strptime(sorted_birthdays[birthday], '%d-%m-%Y').replace(year=datetime.today().year) >= datetime.today() else ((datetime.now().year - datetime.strptime(sorted_birthdays[birthday][-4:], '%Y').year) + 1)} in {days_birthdays[birthday]} days, {datetime.strptime(sorted_birthdays[birthday], '%d-%m-%Y').strftime('%d-%b-%Y')}""",
                inline=False
            )
          
        await ctx.respond(embed=birthdays_embed, ephemeral=True)
    
    
    
    
        
    @tasks.loop(minutes=1)
    async def checkbirthday(self):
        
        checktime = datetime(datetime.today().year, datetime.today().month, datetime.today().day, hour=2, minute=16)
        
        if (checktime <= datetime.now() <= (checktime + timedelta(minutes=10))):
            birthdaysdb = send_sql("SELECT userid, birthday FROM `discord_users` WHERE birthday > 00000000")
            for birthday in birthdaysdb:
                if (datetime.strptime(str(birthday[1]), "%Y-%m-%d").day == datetime.today().day) and (datetime.strptime(str(birthday[1]), "%Y-%m-%d").month == datetime.today().month):
                    birthday_member = self.bot.get_guild(gm_guild_id).get_member(int(birthday[0]))
                    
                    birthday_embed = discord.Embed(
                        title=f"It's {birthday_member.name}'s birthday!",
                        description= f"{birthday_member.name} turned {datetime.now().year - datetime.strptime(str(birthday[1]), '%Y-%m-%d').year} today!",
                        color=0xae8cff
                    )
                    birthday_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/914862282335453215/1067193702038110228/favicon.png")
                    
                    await self.bot.get_channel(882252560608657408).send("@everyone", embed= birthday_embed)
                    
                    
            
def parse_sql(data):
    data = str(data).replace('&', "&#38") #Check &
    data = str(data).replace("'", "&#39") #Check '
    data = str(data).replace('"', "&#34") #Check "
    data = str(data).replace('<', "&#60") #Check <
    data = str(data).replace('>', "&#62") #Check >
    return data

def send_sql(sql):
    GM_db = mysql.connector.connect(
    host= os.getenv('SQL_HOST'),
    user= os.getenv('SQL_USER'),
    password= os.getenv('SQL_PASS'),
    database= os.getenv('SQL_DB')
    )             
    GM_db_cursor = GM_db.cursor() 
        
    GM_db_cursor.execute(sql)
    result = GM_db_cursor.fetchall()
    GM_db.commit()
    GM_db.close()
    return result
    


def setup(bot):
    bot.add_cog(birthday(bot))

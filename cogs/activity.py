
import discord
from discord.ext import commands
from discord.commands import OptionChoice, Option
import discord.utils
from dotenv import load_dotenv
import os
import mysql.connector
from datetime import datetime
from discord.ext import tasks

from cogs.motm import motm

gm_guild_id = 882248303822123018

GMDev_id = 1059968168493318198
GMStaff_id = 1067195296993517568
GMAdmin_id = 882248427298230292
GM_id = 882248832354750524

activity_types = {
    "watching": discord.ActivityType.watching,
    "listening to": discord.ActivityType.listening,
    "playing": discord.ActivityType.playing,
    "competing in": discord.ActivityType.competing,
    "streaming": discord.ActivityType.streaming
}
activitytype_choices = [
    OptionChoice(name="Watching", value="watching"),
    OptionChoice(name="Listening to", value="listening to"),
    OptionChoice(name="Playing", value="playing"),
    OptionChoice(name="Competing in", value="competing in"),
    OptionChoice(name="Streaming", value="streaming")
]

class activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        
        motm_votes = send_sql(f"SELECT month, COUNT(*) AS 'votes' FROM motm_votes WHERE month='{str(datetime.now().month).zfill(2)}' AND year='{datetime.now().year}' GROUP BY month")
        if motm_votes:
            motm_votes = motm_votes[0][1]
        else:
            motm_votes = 0
            
        total_gm = send_sql("SELECT COUNT(*) FROM `discord_users` WHERE rank='Gang Member' OR rank='GM Light'")
        
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"MotM: {motm_votes} / {total_gm} Voted"))
        
        self.refresh_Activity.start()
        
        
        
    # SET ACTIVITY
    @commands.slash_command(name="setactivity", description="Change the bots activity status (STAFF ONLY)")
    @commands.has_any_role(GMStaff_id, GMAdmin_id)
    async def setactivity(self, ctx: discord.ApplicationContext, prefix: Option(input_type=str, name="prefix", description="Choose prefix type", choices=activitytype_choices), text: Option(input_type=str, name="text", description="set text", max_length=14)):
        await self.bot.change_presence(activity=discord.Activity(type=activity_types[prefix], name=text))
        await ctx.respond("Changed activity.", ephemeral=True)
        
    @setactivity.error
    async def motminit_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.respond("You do not have permission to use this command. (STAFF ONLY)", ephemeral=True)
        else:
            raise error
    
    # SET ACTIVITY TO MOTM VOTES
    @commands.slash_command(name="motmactivity", description="Set MotM as activity (STAFF ONLY)")
    @commands.has_any_role(GMStaff_id, GMAdmin_id)
    async def motmactivity(self, ctx: discord.ApplicationContext):
        motm_votes = send_sql(f"SELECT month, COUNT(*) AS 'votes' FROM motm_votes WHERE month='{str(datetime.now().month).zfill(2)}' AND year='{datetime.now().year}' GROUP BY month")
        if motm_votes:
            motm_votes = motm_votes[0][1]
        else:
            motm_votes = 0
        total_gm = send_sql("SELECT rank, COUNT(*) AS 'rank' FROM `discord_users` WHERE rank='Gang Member' GROUP BY rank")[0][1]
        
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"MotM: {motm_votes} / {total_gm} Voted"))
        

    
    
        
    @motmactivity.error
    async def motminit_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.respond("You do not have permission to use this command. (STAFF ONLY)", ephemeral=True)
        else:
            raise error   

    @tasks.loop(minutes=1.0)
    async def refresh_Activity(self):
        await self.motmactivity(self)




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
    bot.add_cog(activity(bot))
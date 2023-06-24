from itertools import count
import discord
from discord.ext import commands
from discord.ext import tasks
import discord.utils
import json
import random
from datetime import datetime, date, timedelta
from dateutil import relativedelta
from collections import defaultdict
from re import sub
from dotenv import load_dotenv
import os
import mysql.connector

#### IDS ####
gm_guild_id = 882248303822123018

motm_channel_id = 1065028419487793182
motm_role_id = 1062507887718567986

GMDev_id = 1059968168493318198
GMStaff_id = 1067195296993517568
GMAdmin_id = 882248427298230292
GM_id = 882248832354750524

load_dotenv()

class motm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.refresh_MOTM.start()
        self.check_for_month.start()
        
    def get_motm(self) -> discord.Member:
        motm = self.bot.get_guild(gm_guild_id).get_role(motm_role_id).members[0]
        return motm

    def votingdaysleft(self):
        voting_days_left = (abs(datetime.today() - ((datetime.today() + (relativedelta.relativedelta(months=1))).replace(day=1, hour= 0, minute= 0, second=1, microsecond= 0)))).days
        return voting_days_left


    #### COUNT VOTES ####
    def count_votes(self, month, year):
        global vote_standings
        # GET ALL VOTES FROM DB IN SELECTED MONTH
        motm_vote_count = send_sql(f"SELECT voted_userid, COUNT(*) AS 'votes' FROM motm_votes WHERE month='{str(month).zfill(2)}' AND year='{year}' GROUP BY voted_userid ORDER BY votes DESC")
        # RETURN LIST OF TUPLES [(userid, count)]
        return motm_vote_count
    
        


    #### GENERATE EMBED ####
    def motm_embed_gen(self):
        motm = self.get_motm()
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
            value=str(self.votingdaysleft()),
            inline=True
        )

        motm_embed.set_footer(text="Use /motmvote @user to vote!")



    #### EDIT EMBED ####
    async def edit_embed(self):
        self.motm_embed_gen()
        
        motm_db = json.load(open('databases/motm.json', encoding="utf-8"))
        motm_db_ID = motm_db[0]["MOTM_Message_ID"]
        
        ch = self.bot.get_channel(motm_channel_id)  
        msg = await ch.fetch_message(motm_db_ID)
        await msg.edit(embed= motm_embed)
        return
        
        
        
        
        
        
    #### INIT MOTM ####
    @commands.slash_command(name="motminit", description="Initialize MOTM (STAFF ONLY)")
    @commands.has_any_role(GMDev_id, GMAdmin_id, GMStaff_id)
    async def motminit(self, ctx: discord.ApplicationContext):
        await ctx.respond("Initializing MOTM", ephemeral=True)
        self.motm_embed_gen() 

        ch = self.bot.get_channel(motm_channel_id)
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
    @commands.slash_command(name="motmdel", description="Purge MOTM channel (DEV ONLY)")
    @commands.has_any_role(GMDev_id)
    async def motmdel(self, ctx: discord.ApplicationContext):

        ch = self.bot.get_channel(motm_channel_id)

        await ctx.respond("Purging", ephemeral=True)
        await ch.purge()
        
        motm_db = json.load(open('databases/motm.json', encoding="utf-8"))
        motm_db[0]["MOTM_Message_ID"] = "0"
        with open('databases/motm.json', 'w') as outfile:
            json.dump(motm_db, outfile, indent=4)


    @tasks.loop(hours=1.0)
    async def refresh_MOTM(self):
        await self.edit_embed()
    
    
    
    
    
    #### VOTE MOTM ####
    @commands.slash_command(name="motmvote", description="Vote for MOTM (GM ONLY)")
    @commands.has_any_role(GM_id)
    async def motmvote(self, ctx: discord.ApplicationContext, vote: str):
        user = ctx.author
        voted_user = self.bot.get_guild(gm_guild_id).get_member(int(sub("[<,>,@]", "", str(vote))))
        
        GM_role = discord.utils.get(ctx.guild.roles, id=GM_id)
        GMadmin_role = discord.utils.get(ctx.guild.roles, id=GMAdmin_id)
        voted_user_model = self.bot.get_guild(gm_guild_id).get_member(int(voted_user.id))
        
        # CHECK IF GM
        if not (GM_role in voted_user_model.roles):
            await ctx.respond("Chosen user is not a GangMember", ephemeral=True)
        # CHECK IF ADMIN
        elif (GMadmin_role in voted_user_model.roles):
            await ctx.respond("Chosen user is an Admin", ephemeral=True)
        # CHECK IF SAME USER
        elif (voted_user == user):
            await ctx.respond("Chosen user is yourself", ephemeral=True)
        #CHECK IF ALREADY VOTED
        elif send_sql(f"SELECT * FROM motm_votes WHERE userid='{user.id}' AND month='{str((datetime.now().month)).zfill(2)}' AND year='{datetime.now().year}'"):
            await ctx.respond("You already voted this month", ephemeral=True)
        #SEND VOTE TO DB
        else:  
            next_vote_id = send_sql("SELECT MAX(id) FROM motm_votes")[0][0] + 1
            send_sql(f"INSERT INTO motm_votes(`id`, `userid`, `username`, `voted_userid`, `voted_username`, `month`, `year`) VALUES ('{next_vote_id}', '{user.id}', '{user.name}', '{voted_user.id}', '{voted_user.name}', '{str((datetime.now().month)).zfill(2)}', '{datetime.now().year}')")
            
            await ctx.respond(f"You voted for <@{voted_user.id}>.", ephemeral=True)
            print(f"{user.name} voted for {voted_user.name} with DB id: {next_vote_id}")
        
                
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
    @commands.slash_command(name="motmstandings", description="View MOTM standings (ADMIN ONLY)")
    @commands.has_any_role(GMAdmin_id, GMDev_id)
    async def motmstandings(self, ctx: discord.ApplicationContext):
        await ctx.respond("\n".join([f"{i}. <@{user[0]}>: **{user[1]}**" for i, user in enumerate(motm.count_votes(self, datetime.now().month, datetime.now().year), start=1)]), ephemeral = True)
        
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
    async def motm_announce(self):
        motmuser = motm.get_motm(self)
        
        
        standings_list = "\n".join([f"{i}. <@{user[0]}>: **{user[1]}**" for i, user in enumerate(vote_standings, start=1)])
        
        motm_announce_embed = discord.Embed(
            title="New Member of the Month",
            color=motmuser.color
        )

        motm_announce_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/914862282335453215/1067193702038110228/favicon.png")
        motm_announce_embed.set_image(url=motmuser.display_avatar.url)
        
        motm_announce_embed.add_field(
            name=f"Our new Member of the month is {motmuser.display_name}!",
            value=f"<@{motmuser.id}> won with {vote_standings[0][1]} votes.",
            inline=False
        )
        

        motm_announce_embed.add_field(
        name="Results:",
        value=standings_list,
        inline=False
        )
        
        await self.bot.get_channel(882252560608657408).send(embed= motm_announce_embed)
        
    #### EDIT MOTM ROLE ####
    async def edit_motm_role(self):
        motmuser = motm.get_motm(self)
        motm_role = self.bot.get_guild(gm_guild_id).get_role(motm_role_id)
        
        await motmuser.remove_roles(motm_role)
        await self.bot.get_guild(gm_guild_id).get_member(int(vote_standings[0][0])).add_roles(motm_role)
    

    #### CHECK FOR NEW MONTH ####
    @tasks.loop(minutes=1)
    async def check_for_month(self):

        motm_month = (date.today().month)
        first_of_month = datetime(date.today().year, motm_month, 1, hour=0, minute=1)
        
        if (first_of_month <= datetime.now() <= (first_of_month + timedelta(minutes=1))):
            self.count_votes()
            if vote_standings[0][1] == vote_standings[1][1]:
                if random.randint(1,2) == 2:
                    vote_standings[0],vote_standings[1] = vote_standings[1],vote_standings[0]
                    
            await self.edit_motm_role()
            await self.motm_announce()
            motm.reset_voting()
            await self.refresh_MOTM()
            
            
            
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
    bot.add_cog(motm(bot))
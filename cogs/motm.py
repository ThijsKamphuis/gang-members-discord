import discord
from discord.ext import commands
from discord.ext import tasks
import discord.utils
import json
import random
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
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
GMLight_id = 1191905861770154048


load_dotenv()


class motm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.refresh_MOTM.start()
        self.check_for_month.start()
        await self.edit_motm_role()
        await self.motm_announce()
        await self.refresh_MOTM()
        
    def get_motm(self) -> discord.Member:
        motm = self.bot.get_guild(gm_guild_id).get_role(motm_role_id).members[0]
        return motm

    def votingdaysleft(self):
        voting_days_left = (abs(datetime.today() - ((datetime.today() + (relativedelta(months=1))).replace(day=1, hour= 0, minute= 0, second=1, microsecond= 0)))).days
        return voting_days_left


    #### COUNT VOTES ####
    def count_votes(self, month, year):
        # GET ALL VOTES FROM DB IN SELECTED MONTH
        motm_vote_count = send_sql(f"SELECT voted_userid, COUNT(*) AS 'votes' FROM motm_votes WHERE month='{str(month).zfill(2)}' AND year='{year}' GROUP BY voted_userid ORDER BY votes DESC")
        # RETURN LIST OF TUPLES [(userid, count)]
        return motm_vote_count
    


        


    #### GENERATE EMBED MOTM ####
    def motm_embed_gen(self):
        motm = self.get_motm()
        global motm_embed
        motm_embed = discord.Embed(
            title="Member of the Month",
            color=motm.color
        )

        motm_embed.set_thumbnail(url="https://gangmembers.eu/img/favicon/android-chrome-512x512.png")
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



    #### EDIT EMBED MOTM ####
    async def edit_embed(self):
        self.motm_embed_gen()
        
        motm_message_id = send_sql(f"SELECT message_id FROM motm_data")[0][0]
        
        ch = self.bot.get_channel(motm_channel_id)  
        msg = await ch.fetch_message(motm_message_id)
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

        send_sql(f"UPDATE motm_data SET message_id='{motm_message.id}'")
        

    @motminit.error
    async def motminit_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.respond("You do not have permission to use this command. (STAFF ONLY)", ephemeral=True)
        else:
            raise error




    #### DEL EMBED MOTM ####
    @commands.slash_command(name="motmdel", description="Purge MOTM channel (DEV ONLY)")
    @commands.has_any_role(GMDev_id)
    async def motmdel(self, ctx: discord.ApplicationContext):

        ch = self.bot.get_channel(motm_channel_id)

        await ctx.respond("Purging...", ephemeral=True)
        await ch.purge()
        
        send_sql(f"UPDATE motm_data SET message_id='0'")



    @tasks.loop(hours=1.0)
    async def refresh_MOTM(self):
        await self.edit_embed()
    
    
    
    
    
    #### VOTE MOTM ####
    @commands.slash_command(name="motmvote", description="Vote for MOTM (GM ONLY)")
    @commands.has_any_role(GM_id, GMLight_id)
    async def motmvote(self, ctx: discord.ApplicationContext, vote: str):
        user = ctx.author
        voted_user = self.bot.get_guild(gm_guild_id).get_member(int(sub("[!,<,>,@]", "", str(vote))))
        
        GM_role = discord.utils.get(ctx.guild.roles, id=GM_id)
        GMadmin_role = discord.utils.get(ctx.guild.roles, id=GMAdmin_id)
        GMlight_role = discord.utils.get(ctx.guild.roles, id=GMLight_id)
        voted_user_model = self.bot.get_guild(gm_guild_id).get_member(int(voted_user.id))
        
        # CHECK IF GM
        if not (GM_role in voted_user_model.roles):
            await ctx.respond("Chosen user is not a GangMember", ephemeral=True)
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
            
            motm_votes = send_sql(f"SELECT month, COUNT(*) AS 'votes' FROM motm_votes WHERE month='{str(datetime.now().month).zfill(2)}' AND year='{datetime.now().year}' GROUP BY month")[0][1]
            total_gm = send_sql("SELECT COUNT(*) FROM `discord_users` WHERE rank='Gang Member' OR rank='GM Light'")[0][0]
            
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"MotM: {motm_votes} / {total_gm} Voted"))
            
            
            
            
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
    
    
            
    #### ANNOUNCE MOTM ####       
    async def motm_announce(self):
        motmuser = motm.get_motm(self)
        
        prev_month = datetime.now().month - 1
        if prev_month == 0:
            prev_month = 12
            year = datetime.now().year - 1
        else:
            year = datetime.now().year
                
        motm_vote_count = self.count_votes(prev_month, year)
        
        
        standings_list = "\n".join([f"{i}. <@{user[0]}>: **{user[1]}**" for i, user in enumerate(motm_vote_count, start=1)])
        
        motm_announce_embed = discord.Embed(
            title="New Member of the Month",
            color=motmuser.color
        )

        motm_announce_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/914862282335453215/1067193702038110228/favicon.png")
        motm_announce_embed.set_image(url=motmuser.avatar.url)
        
        motm_announce_embed.add_field(
            name="Our new Member of the month is:",
            value=f"<@{motmuser.id}>!! They won with {motm_vote_count[0][1]} votes.",
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
        
        motm_vote_count = motm.count_votes(self, (date.today() - relativedelta(months=1)).month, datetime.now().year)
        
        await motmuser.remove_roles(motm_role)
        await self.bot.get_guild(gm_guild_id).get_member(int(motm_vote_count[0][0])).add_roles(motm_role)
    

    #### CHECK FOR NEW MONTH ####
    @tasks.loop(minutes=1)
    async def check_for_month(self):
        # FIRST MINUTE OF FIRST DAY OF MONTH
        first_of_month = datetime(date.today().year, date.today().month, 1, hour=0, minute=1)
        # CHECK IF IN FIRST OF MONTH
        if (first_of_month <= datetime.now() <= (first_of_month + timedelta(minutes=1))):
            # COUNT VOTES
            motm_vote_count = motm.count_votes(self, (date.today() - relativedelta(months=1)).month, datetime.now().year)
            # IF TOP 2 TIED
            if motm_vote_count[0][1] == motm_vote_count[1][1]:
                # COINFLIP
                if random.randint(1,2) == 2:
                    motm_vote_count[0],motm_vote_count[1] = motm_vote_count[1],motm_vote_count[0]
                    
            await self.edit_motm_role()
            await self.motm_announce()
            await self.refresh_MOTM()
            
            # ADD MOTM TO DATABASE
            motmmember = self.bot.get_guild(gm_guild_id).get_member(int(motm_vote_count[0][0]))
            next_motmid = send_sql("SELECT MAX(motmid) FROM motm")[0][0] + 1
            
            send_sql(f"INSERT INTO motm (motmid, userid, username, month, year) VALUES ('{next_motmid}', '{motmmember.id}', '{motmmember.name}', '{str(datetime.now().month).zfill(2)}', '{datetime.now().year}')")
    
 
 
            
            
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
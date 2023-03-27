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


#### IDS ####
gm_guild_id = 882248303822123018

motm_channel_id = 1065028419487793182
motm_role_id = 1062507887718567986

GMDev_id = 1059968168493318198
GMStaff_id = 1067195296993517568
GMAdmin_id = 882248427298230292
GM_id = 882248832354750524



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
    def count_votes(self):
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
    async def motmvote(self, ctx: discord.ApplicationContext, user: str):
        voter = sub("[<,>,@]", "", str(ctx.author.id))
        user = sub("[<,>,@]", "", str(user))
        
        GM_role = discord.utils.get(ctx.guild.roles, id=GM_id)
        GMadmin_role = discord.utils.get(ctx.guild.roles, id=GMAdmin_id)
        user_model = self.bot.get_guild(gm_guild_id).get_member(int(user))
        
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
        
        await self.refresh_MOTM()
        
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
    @commands.has_any_role(GMAdmin_id)
    async def motmstandings(self, ctx: discord.ApplicationContext):
        await ctx.respond("\n".join([f"{i}. <@{user[0]}>: **{user[1]}**" for i, user in enumerate(motm.count_votes(self), start=1)]), ephemeral = True)
        
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
        motm = motm.get_motm()
        
        
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
        
        await self.bot.get_channel(882252560608657408).send(embed= motm_announce_embed)
        
    #### EDIT MOTM ROLE ####
    async def edit_motm_role(self):
        motm = motm.get_motm()
        motm_role = self.bot.get_guild(gm_guild_id).get_role(motm_role_id)
        
        await motm.remove_roles(motm_role)
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
            self.reset_voting()
            await self.refresh_MOTM()
        
def setup(bot):
    bot.add_cog(motm(bot))
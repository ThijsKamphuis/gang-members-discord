import discord
from discord.ext import commands
import discord.utils
import os
from dotenv import load_dotenv
from num2words import num2words

#### SETUP ###################################################
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

#### STARTUP ###################################################
@bot.event
async def on_connect():
    bot.load_extension("cogs.noterix")
    bot.load_extension("cogs.gifs")
    bot.load_extension("cogs.quote")
    bot.load_extension("cogs.motm")
    await bot.sync_commands()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="polish moments"))
    bot.add_view(GameRoleSelectMenu())
    
    
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
            discord.SelectOption(label = "Counter Strike: Global Offensive", emoji = game_logos["logo_csgo"]),           
            discord.SelectOption(label = "ARK: Survival Evolved",emoji = game_logos["logo_ark"]),
            discord.SelectOption(label = "Grand Theft Auto V",emoji = game_logos["logo_gtav"]),
            discord.SelectOption(label = "Minecraft",emoji = game_logos["logo_mc"]),
            discord.SelectOption(label = "Left 4 Dead 2",emoji = game_logos["logo_l4d2"]),
            discord.SelectOption(label = "Among Us",emoji = game_logos["logo_amongus"]),
            discord.SelectOption(label = "Project Zomboid",emoji = game_logos["logo_zomboid"]),
            discord.SelectOption(label = "Genshin Impact",emoji = game_logos["logo_genshin"]),
            discord.SelectOption(label = "Hearts of Iron IV",emoji = game_logos["logo_hoi4"]),
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










bot.run(os.getenv('DISCORD_TOKEN'))

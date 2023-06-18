import discord
import discord.utils
import os
from dotenv import load_dotenv
from num2words import num2words
import requests
import json
import mysql.connector
import paramiko

from cogs.old.roles import roles

#### SETUP ####
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
Regular_id = 1065394897835794453
NPC_id = 882251536653230151
Bot_id = 882253119063470133

special_roles = [
    882248427298230292,  #GM Admin
    1062507887718567986, #MotM
    1088792450950238229, #Chess Champion
    1067195296993517568, #GM Staff
    910637039605657600,  #Moderator
    1059968168493318198, #GM Dev
    1054113909268819998, #roze
    894648458881925143,  #Meerwaardige
    1068524190321344573, #OG MotM
    1096558106495954975, #GM Rep
    1113075406896115873, #GM Sponsor
    1118107466085970010, #Senshi
    1091490581512982578, #Ankerd
    1065022590298620015, #C reload
    1116098626603716609, #Vis van de dag
    1100852249187594260, #Background NPC
]

#### STARTUP ####
@bot.event
async def on_connect():
    bot.load_extension("cogs.gifs")
    bot.load_extension("cogs.quote")
    bot.load_extension("cogs.motm")
    bot.load_extension("cogs.activity")
    bot.load_extension("cogs.birthday")
    await bot.sync_commands()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')




#### ON MEMBER JOIN ####
@bot.event
async def on_member_join(member):
    await member.add_roles(bot.get_guild(gm_guild_id).get_role(882251536653230151))
    member_count = bot.get_guild(gm_guild_id).member_count
    count_suffix = num2words(member_count, to='ordinal')[-2:]
    if (member_count % 100) == 0:
        await bot.get_channel(882248303822123021).send(f"Congratulations <@{member.id}>, welcome to Gang Members. You are the {member_count}{count_suffix} member to join!!!!!!")
    else:
        await bot.get_channel(882248303822123021).send(f"Hello <@{member.id}>, welcome to Gang Members. You are the {member_count}{count_suffix} member to join.")
    download_user_pfp(member)
    upload_user_pfp(member)
    upload_member(member)
    
#### ON MEMBER LEAVE ####
@bot.event
async def on_member_remove(member):    
    birthdaysdb = json.load(open('databases/birthdays.json', encoding="utf-8"))
    if str(member.id) in birthdaysdb.keys():
        birthdaysdb.pop(str(member.id))
    
    motmvotesdb = json.load(open('databases/motm_votes.json', encoding="utf-8"))
    for vote in motmvotesdb:
        if str(member.id) in vote["Vote"] or str(member.id) in vote["User"]:
            motmvotesdb.remove(vote)
        
    with open('databases/birthdays.json', 'w') as outfile:
        json.dump(birthdaysdb, outfile, indent=4)
    with open('databases/motm_votes.json', 'w') as outfile:
        json.dump(motmvotesdb, outfile, indent=4)
        
    os.remove(f"profilepics/{member.name}.png")
    delete_user_pfp(member)
    delete_member(member)



#### AUTO UPDATE DATABASES #### 
@bot.event
async def on_member_update(before, after):
    download_user_pfp(after)
    upload_user_pfp(after) 
    update_member(after)
  
@bot.event
async def on_user_update(before, after):
    download_user_pfp(after)
    upload_user_pfp(after)
    update_member(after)
  
@bot.event
async def on_guild_role_update(before, after):
    for member in bot.get_guild(gm_guild_id).get_role(after.id).members:
        update_member(member)


   
#### PROFILE PICS ####
def download_all_pfps():
    for member in (bot.get_guild(gm_guild_id).members):
        print(member.name)
        if member.avatar == None:
            open(f"profilepics/{member.name}.png", "wb").write(requests.get(member.display_avatar.url, allow_redirects=True).content)
        else:
            open(f"profilepics/{member.name}.png", "wb").write(requests.get(member.avatar.url, allow_redirects=True).content)      


def download_user_pfp(member):
    if member.avatar == None:
        open(f"profilepics/{member.name}.png", "wb").write(requests.get(member.display_avatar.url, allow_redirects=True).content)
    else:
        open(f"profilepics/{member.name}.png", "wb").write(requests.get(member.avatar.url, allow_redirects=True).content)


def upload_all_pfps():
    GM_sftp, transport = open_sftp()
    
    files = os.listdir("profilepics")
    for pfp in files:
        GM_sftp.put(f"profilepics/{pfp}", f"img/discord_upload/profilepics/{pfp}")
    transport.close()
    print("Uploaded all Pfps")

def upload_user_pfp(member):
    GM_sftp, transport = open_sftp()
    
    GM_sftp.put(f"profilepics/{member.name}.png", f"img/discord_upload/profilepics/{member.name}.png")
    transport.close()
    print(f"Uploaded {member.name}.png")

def delete_user_pfp(member):
    GM_sftp, transport = open_sftp()
    
    GM_sftp.remove(f"img/discord_upload/profilepics/{member.name}.png")

    transport.close()
    print(f"Deleted {member.name}.png")
    
def open_sftp():
    transport = paramiko.Transport((os.getenv("SFTP_HOST"), 22))
    transport.connect(username= os.getenv("SFTP_USER"), password= os.getenv("SFTP_PASS"))
    GM_sftp = paramiko.SFTPClient.from_transport(transport)    
    return GM_sftp, transport
     
     
#### MEMBERS SQL ####
memberlist = []

def get_all_members():
    for member in (bot.get_guild(gm_guild_id).members):
        rank, roles = format_roles(member)
                
        memberinfo = {
            "username": member.name,
            "userid": member.id,
            "rank": rank,
            "roles": roles,
            "avatarurl": f"https://gangmembers.eu/img/discord_upload/profilepics/{member.name}.png"
        }
        memberlist.append(memberinfo)
    print("Fetched all members")
        
def upload_all_members():
    for member in memberlist:
        send_sql(f"INSERT INTO discord_users(userid, username, rank, roles, avatarurl) VALUES ({parse_sql(member['userid'])}, '{parse_sql(member['username'])}', '{parse_sql(member['rank'])}', '{parse_sql(member['roles'])}', '{parse_sql(member['avatarurl'])}')")
    print("Uploaded all members")
    
def update_all_members():
    for member in memberlist:
        send_sql(f"UPDATE discord_users SET username = '{parse_sql(member['username'])}', rank = '{parse_sql(member['rank'])}', roles = '{parse_sql(member['roles'])}', avatarurl = '{parse_sql(member['avatarurl'])}' WHERE userid = {parse_sql(member['userid'])}")
    print("Updated all members")
        
def upload_member(member):
    rank, roles = format_roles(member)
    send_sql(f"INSERT INTO discord_users(userid, username, rank, roles, avatarurl) VALUES ({parse_sql(member.id)}, '{parse_sql(member.name)}', '{parse_sql(rank)}', '{parse_sql(roles)}', '{parse_sql(f'https://gangmembers.eu/img/discord_upload/profilepics/{member.name}.png')}')")
    print(f"Uploaded {member.name}") 
      
def update_member(member):
    
    member = bot.get_guild(gm_guild_id).get_member(member.id)
     
    rank, roles = format_roles(member)
    send_sql(f"UPDATE discord_users SET username = '{parse_sql(member.name)}', rank = '{parse_sql(rank)}', roles = '{parse_sql(roles)}', avatarurl = '{parse_sql(f'https://gangmembers.eu/img/discord_upload/profilepics/{member.name}.png')}' WHERE userid = '{parse_sql(member.id)}'") 
    print(f"Updated {member.name}")
    
def delete_member(member): 
    send_sql(f"DELETE FROM discord_users WHERE userid='{parse_sql(member.id)}'")
    print(f"Deleted {member.id}")







def format_roles(member):
    if member.top_role.id == GM_id or member.top_role.id == Regular_id or member.top_role.id == NPC_id or member.top_role.id == Bot_id:
        rank = member.top_role.name
        roles = ''
    else:
        rolelist = []
        for role in member.roles:
            if role.id in special_roles:
                rolelist.append(role.name)
        rolelist.reverse()
        roles = ", ".join(rolelist)
        
        if bot.get_guild(gm_guild_id).get_role(GM_id) in member.roles:
            rank = bot.get_guild(gm_guild_id).get_role(GM_id).name
        elif bot.get_guild(gm_guild_id).get_role(Regular_id) in member.roles:
            rank = bot.get_guild(gm_guild_id).get_role(Regular_id).name
        elif bot.get_guild(gm_guild_id).get_role(NPC_id) in member.roles:
            rank = bot.get_guild(gm_guild_id).get_role(NPC_id).name
        elif bot.get_guild(gm_guild_id).get_role(Bot_id) in member.roles:
            rank = bot.get_guild(gm_guild_id).get_role(Bot_id).name
        else:
            rank = ''
        
    return rank, roles


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
    GM_db.commit()
    GM_db.close()







#Manual upload for old archive json
def manual_upload():
    id = 35
    votes = []
    for vote in votes:
        send_sql(f"INSERT INTO motm_votes(`id`, `userid`, `username`, `voted_userid`, `voted_username`, `month`, `year`) VALUES ('{id}', '{vote['User']}', '{bot.get_guild(gm_guild_id).get_member(int(vote['User'])).name}', '{vote['Vote']}', '{bot.get_guild(gm_guild_id).get_member(int(vote['Vote'])).name}', '05', '2023')")
        id += 1
            
bot.run(os.getenv('DISCORD_TOKEN'))

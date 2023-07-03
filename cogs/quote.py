from ast import parse
import discord
from discord.ext import commands
import discord.utils
import json
import random
import math
import mysql.connector
import os

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

def get_quote_page(page):
        quote_list = send_sql("SELECT * FROM quotes ORDER BY id ASC")

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
                    name=quote_list[quoteindex][2],
                    value=f'{quote_list[quoteindex][1]}, {quote_list[quoteindex][3]}  `id:{quote_list[quoteindex][0]}`\n \u200B',
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
                    name=quote_list[quoteindex][2],
                    value=f'{quote_list[quoteindex][1]}, {quote_list[quoteindex][3]}  `id:{quote_list[quoteindex][0]}`\n \u200B',
                    inline=False
                )
                quoteindex += 1
                
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
            
        
class quote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    #### QUOTE RANDOM ####
    @commands.slash_command(name="quote", description='Random Gang Member Quote')
    async def gmquote(self, ctx: discord.ApplicationContext):
        gm_quote = random.sample(send_sql("SELECT * FROM quotes"), 1)[0]
        await ctx.respond(f'> {gm_quote[2]}\n**~{gm_quote[1]}, {gm_quote[3]}**')


    #### QUOTE ADD ####
    @commands.slash_command(name="quoteadd", description='Add a Gang Member Quote (GM Only)')
    @commands.has_any_role(GM_id)
    async def gmquoteadd(self, ctx: discord.ApplicationContext, quote: str, author: str, year: int):
        next_quote_id = send_sql("SELECT MAX(id) FROM quotes")[0][0] + 1
        
        send_sql(f"INSERT INTO `quotes` (`id`, `author`, `quote`, `year`) VALUES ('{next_quote_id}', '{parse_sql(author)}', '{parse_sql(quote)}', '{parse_sql(year)}')")
        await ctx.respond(f'> {quote}\n**{author}, {year}**\n Quote successfully added!', ephemeral=True)

    #### QUOTE LIST ####
    @commands.slash_command(name="quotelist", description='List all Gang Member Quotes')
    async def gmquotelist(self, ctx: discord.ApplicationContext):
        get_quote_page(1)
        await ctx.respond(embed = quote_embed, view = QuoteButtonsView(), ephemeral=True)

    #### QUOTE DEL ####
    @commands.slash_command(name="quotedel", description='Delete a Gang Member Quote (STAFF Only)')
    @commands.has_any_role(GMStaff_id, GMDev_id, GMAdmin_id)
    async def gmquotedel(self, ctx: discord.ApplicationContext, id: int):
        id_quote = send_sql(f"SELECT * FROM quotes WHERE id='{id}'")[0]
        
        send_sql(f"DELETE FROM quotes WHERE id='{id}'")
        
        await ctx.respond(f'> {id_quote[2]}\n**{id_quote[1]}, {id_quote[3]}**\n Quote successfully deleted!', ephemeral=True)
        
    
        
        
        
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
    bot.add_cog(quote(bot))

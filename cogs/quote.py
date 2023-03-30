import discord
from discord.ext import commands
import discord.utils
import json
import random
import math

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
        gm_quote = random.sample(json.load(open('databases/quotes.json', encoding="utf-8")), 1)[0]
        await ctx.respond(f'> {gm_quote["Quote"]}\n**~{gm_quote["Author"]}, {gm_quote["Year"]}**')


    #### QUOTE ADD ####
    @commands.slash_command(name="quoteadd", description='Add a Gang Member Quote')
    async def gmquoteadd(self, ctx: discord.ApplicationContext, quote: str, author: str, year: int):     
        quotelist = json.load(open('databases/quotes.json', encoding="utf-8"))
        quotelist.append({"Quote":quote,"Author":author,"Year":year})
        with open('databases/quotes.json', 'w') as outfile:
            json.dump(quotelist, outfile, indent=4)

        await ctx.respond(f'> {quote}\n**~{author}, {year}**\n Quote successfully added!')

    #### QUOTE LIST ####
    @commands.slash_command(name="quotelist", description='List all Gang Member Quotes')
    async def gmquotelist(self, ctx: discord.ApplicationContext):
        get_quote_page(1)
        await ctx.respond(embed = quote_embed, view = QuoteButtonsView(), ephemeral=True)

        
def setup(bot):
    bot.add_cog(quote(bot))
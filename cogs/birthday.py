import discord
from discord.ext import commands
import discord.utils
import json
from datetime import datetime

class birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @commands.slash_command(name="birthdayset", description="Add your birthday to the Gang Members calendar.")
    async def birthdayset(self, ctx: discord.ApplicationContext, day: int, month: int, year: int):
        birthdaysdb = json.load(open('databases/birthdays.json', encoding="utf-8"))
        if datetime.strptime(f"{day:02d}-{month:02d}-{year}", "%d-%m-%Y"):
            birthdaysdb[f'{ctx.user.id}'] = f"{day:02d}-{month:02d}-{year}"
            await ctx.respond(f"Set {day:02d}-{month:02d}-{year} as your birthday.", ephemeral=True)
        else:
            ctx.respond("Wrong format, dd-mm-YYYY")
            return
            
        with open('databases/birthdays.json', 'w') as outfile:
                json.dump(birthdaysdb, outfile, indent=4)
                
        
            
        
def setup(bot):
    bot.add_cog(birthday(bot))
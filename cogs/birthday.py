import discord
from discord.ext import commands
import discord.utils
import json
from datetime import datetime


gm_guild_id = 882248303822123018

class birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @commands.slash_command(name="setbirthday", description="Add your birthday to the Gang Members calendar.")
    async def setbirthday(self, ctx: discord.ApplicationContext, day: int, month: int, year: int):
        birthdaysdb = json.load(open('databases/birthdays.json', encoding="utf-8"))
        
        if datetime.strptime(f"{day:02d}-{month:02d}-{year}", "%d-%m-%Y"):
            birthdaysdb[f'{ctx.user.id}'] = f"{day:02d}-{month:02d}-{year}"
            await ctx.respond(f"Set {day:02d}-{month:02d}-{year} as your birthday.", ephemeral=True)
        else:
            ctx.respond("Wrong format, dd-mm-yyyy")
            return
            
        with open('databases/birthdays.json', 'w') as outfile:
                json.dump(birthdaysdb, outfile, indent=4)
                
                

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
        
        


def setup(bot):
    bot.add_cog(birthday(bot))
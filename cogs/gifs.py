import discord
from discord.ext import commands
import discord.utils
import random
import json

class gifs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    #### 727 GIF ####
    @commands.slash_command(name="727", description='727?')
    async def gif727(self, ctx: discord.ApplicationContext):
        await ctx.respond(random.sample(json.load(open('databases/gifs.json', encoding="utf-8")), 1)[0])
        return    

    #### JORN GIF ####
    @commands.slash_command(name="vallas", description='JORN (VALLAS)')
    async def jorngif(self, ctx: discord.ApplicationContext):
        await ctx.respond("https://tenor.com/view/jorn-discord-mod-letterlijk-jorn-gif-27345172")
        return    

    #### MANOE GIF ####
    @commands.slash_command(name="manoe", description='MANOE')
    async def manoegif(self, ctx: discord.ApplicationContext):
        await ctx.respond("https://tenor.com/view/manoe-gangmembers-gm-gif-27494707")
        return
    
    #### MANOE GIF ####
    @commands.slash_command(name="bram", description='BRAM')
    async def bramgif(self, ctx: discord.ApplicationContext):
        await ctx.respond("https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExODhhZmI4MDRhN2JlNzFmOGUzYmFkYWFiZWFiYzY2NjMxODU1Nzg1YyZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/4tFyr7OuPTtPC1VFve/giphy.gif")
        return   


        
def setup(bot):
    bot.add_cog(gifs(bot))
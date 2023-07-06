import discord
from discord.ext import commands
import discord.utils
import random
import json

class gifs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
    
    #### BRAM GIF ####
    @commands.slash_command(name="bram", description='BRAM')
    async def bramgif(self, ctx: discord.ApplicationContext):
        await ctx.respond("https://i.giphy.com/media/4tFyr7OuPTtPC1VFve/giphy.webp")
        return   

    #### FADE GIF ####
    @commands.slash_command(name="fade", description='FADE')
    async def fadegif(self, ctx: discord.ApplicationContext):
        await ctx.respond("https://i.giphy.com/media/pVUHGrgD2wbUPDDHTL/giphy.mp4")
        return 

        
def setup(bot):
    bot.add_cog(gifs(bot))
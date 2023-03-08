
import discord
from discord.ext import commands
from discord.commands import OptionChoice, Option
import discord.utils
import random
import json

GMDev_id = 1059968168493318198
GMStaff_id = 1067195296993517568
GMAdmin_id = 882248427298230292
GM_id = 882248832354750524

activity_types = {
    "watching": discord.ActivityType.watching,
    "listening to": discord.ActivityType.listening,
    "playing": discord.ActivityType.playing,
    "competing in": discord.ActivityType.competing,
    "streaming": discord.ActivityType.streaming
}
activitytype_choices = [
    OptionChoice(name="Watching", value="watching"),
    OptionChoice(name="Listening to", value="listening to"),
    OptionChoice(name="Playing", value="playing"),
    OptionChoice(name="Competing in", value="competing in"),
    OptionChoice(name="Streaming", value="streaming")
]

class activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        # SET CURRENT ACTIVITY
        current_activity = json.load(open('databases/activity.json', encoding="utf-8"))["current"][0]
        await self.bot.change_presence(activity=discord.Activity(type=activity_types[current_activity["type"]], name=current_activity["name"]))
        
        
    # SET ACTIVITY
    @commands.slash_command(name="setactivity", description="Change the bots activity status")
    @commands.has_any_role(GMStaff_id, GMAdmin_id)
    async def setactivity(self, ctx: discord.ApplicationContext, prefix: Option(input_type=str, name="prefix", description="Choose prefix type", choices=activitytype_choices), text: Option(input_type=str, name="text", description="set text", max_length=14)):
        await self.bot.change_presence(activity=discord.Activity(type=activity_types[prefix], name=text))
        
        activitylist = json.load(open('databases/activity.json', encoding="utf-8"))
        activitylist["current"][0]["type"], activitylist["current"][0]["name"] = prefix, text
        with open('databases/activity.json', 'w') as outfile:
            json.dump(activitylist, outfile, indent=4)
        await ctx.respond("Changed activity.", ephemeral=True)
        
    @setactivity.error
    async def motminit_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.respond("You do not have permission to use this command. (STAFF ONLY)", ephemeral=True)
        else:
            raise error
    
    # SAVE CURRENT ACTIVITY
    @commands.slash_command(name="saveactivity", description="Save the current activity")
    @commands.has_any_role(GMStaff_id, GMAdmin_id)
    async def saveactivity(self, ctx: discord.ApplicationContext):
        
        activitylist = json.load(open('databases/activity.json', encoding="utf-8"))
        activitylist["list"].append({"type":activitylist["current"][0]["type"],"name":activitylist["current"][0]["name"]})
        with open('databases/activity.json', 'w') as outfile:
            json.dump(activitylist, outfile, indent=4)        
        
        await ctx.respond("Activity saved.", ephemeral=True)
        
    @saveactivity.error
    async def motminit_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.respond("You do not have permission to use this command. (STAFF ONLY)", ephemeral=True)
        else:
            raise error   

def setup(bot):
    bot.add_cog(activity(bot))
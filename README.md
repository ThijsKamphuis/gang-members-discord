![Discord Shield](https://discordapp.com/api/guilds/882248303822123018/widget.png?style=shield)

OFFICIAL GANG MEMBERS DISCORD BOT
=====================================
[![GANG MEMBERS DISCORD](https://img.shields.io/badge/GANG_MEMBERS_DISCORD-5865F2?style=for-the-badge)](https://dc.gangmembers.eu)
[![GANGMEMBERS.EU](https://img.shields.io/badge/GANGMEMBERS.EU-ae8cff?style=for-the-badge)](https://gangmembers.eu)

ABOUT THE BOT
=============
This bot is used for programming miscellaneous commands to improve the servers feel and personality. 

FUNCTIONS
---------
**727** `/727`<br>
Sends a random 727 related gif in the channel the command is issued.
It uses a .json file to store the relevant links. <br>
```python
@bot.slash_command(name="727", guild_ids=[GUILD], description='727?')
async def gif727(ctx):
    await ctx.respond(random.sample(json.load(open('gifs.json')), 1)[0])
    return    
```

<br>

**Random Quote** `/gmquote` <br>
Sends a random Gang Member quote in the channel the command is issued.
All of the quotes are stored in a .json list of dictionaries that contain quote, author and year.<br>
```python
@bot.slash_command(name="gmquote", guild_ids=[GUILD], description='Random Gang Member Quote')
async def gmquote(ctx):
    gm_quote = random.sample(json.load(open('quotes.json')), 1)[0]
    await ctx.respond(f'> {gm_quote["Quote"]}\n**~{gm_quote["Author"]}, {gm_quote["Year"]}**')  
```
It's also possible to add custom quotes to the database.
This is done using the `/gmquoteadd` command. <br>
```python
@bot.slash_command(name="gmquoteadd", guild_ids=[GUILD], description='Add a Gang Member Quote')
async def gmquote(ctx: discord.ApplicationContext, quote: str, author: str, year: int):
    
    quotelist = json.load(open('quotes.json'))
    quotelist.append({"Quote":quote,"Author":author,"Year":year})    
    with open('quotes.json', 'w') as outfile:
        json.dump(quotelist, outfile)
        
    await ctx.respond(f'> {quote}\n**~{author}, {year}**\n Quote successfully added!')
```

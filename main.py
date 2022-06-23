import os
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='cb ', intents=discord.Intents.all())

async def load_cogs(bot):
    for file in os.listdir('cogs'):
        if file.endswith('.py'):
            await bot.load_extension(file)

@bot.event
async def on_ready():
    await load_cogs(bot)
    print(f"Logged in as {bot.user}")

bot.run(os.environ["DISCORD_TOKEN"])

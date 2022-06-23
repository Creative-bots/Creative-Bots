import os
import discord
from discord.ext import commands
import argparse

# Add an argument parser to handle production and development mode
parser = argparse.ArgumentParser(description="Discord bot for the Discord server")
parser.add_argument("--dev", action="store_true", help="Run the bot in development mode")
args = parser.parse_args()

if args.dev:
    import dotenv
    dotenv.load_dotenv()
    

bot = commands.Bot(command_prefix='cb ', intents=discord.Intents.all())

async def load_cogs(bot):
    for file in os.listdir('cogs'):
        if file.endswith('.py'):
            await bot.load_extension('cogs/'+file)

@bot.event
async def on_ready():
    await load_cogs(bot)
    print(f"Logged in as {bot.user}")

bot.run(os.environ.get("DISCORD_TOKEN"))

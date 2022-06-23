# This example requires the 'message_content' privileged intents

import os
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='cb ', intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(os.environ["DISCORD_TOKEN"])

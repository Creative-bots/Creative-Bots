import os
import discord
from discord.ext import commands
import argparse
import asyncpg
from github import Github

# Add an argument parser to handle production and development mode
parser = argparse.ArgumentParser(description="Discord bot for the Discord server")
parser.add_argument("--dev", action="store_true", help="Run the bot in development mode")
args = parser.parse_args()

if args.dev:
    import dotenv
    dotenv.load_dotenv()


class Manager(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='cb ',
            intents=discord.Intents.all()
        )
        self.github = Github(os.environ.get("GITHUB_TOKEN"))

    # Startup Functions
    async def load_cogs(self):
        print("Loading cogs...")
        for file in os.listdir(os.getcwd() + '/bot/cogs'):
            if file.endswith('.py') and file != '__init__.py':
                await self.load_extension('cogs.' + file[:-3])
                print(f"Loaded {file}")

        os.environ.setdefault("JISHAKU_NO_UNDERSCORE", "1") 
        os.environ.setdefault("JISHAKU_HIDE", "1")
        await self.load_extension('jishaku')
        print("Loaded jiskau")

    async def create_pool(self):
        self.db = await asyncpg.create_pool(dsn=os.environ.get("DB_DSN"))

        await self.db.execute('CREATE TABLE IF NOT EXISTS ideas (idea_owner_id BIGINT, idea TEXt, idea_name TEXT, idea_code TEXT, status TEXT, idea_message_id BIGINT)')
        await self.db.execute('CREATE TABLE IF NOT EXISTS github_names (user_id BIGINT, github_name TEXT)')

    async def on_connect(self):
        print(f"Connected to Discord as {self.user}")
        await self.load_cogs()
        await self.create_pool()

    async def on_ready(self):
        print("Manager is ready!")

    # Server and bot properties
    @property
    def dev_category(self) -> discord.CategoryChannel:
        return self.get_channel(988221364886462486)

    @property
    def archive_category(self) -> discord.CategoryChannel:
        return self.get_channel(989723651714736189)

    @property
    def guild(self) -> discord.Guild:
        return self.get_guild(985700466937696288)


if __name__ == '__main__':
    bot = Manager()
    bot.run(os.environ.get("DISCORD_TOKEN"))

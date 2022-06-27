import discord
from discord.ext import commands

from bot.helpers.embeds import Success, Error, ManagerEmbed as Embed

import github

class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        embed = Embed(
            title="Pong! 🏓",
            description=f"Current client latency: {self.bot.latency * 1000:.0f}ms",
            color=discord.Color.dark_theme()
        )

        embed.default_footer(ctx)

        await ctx.send(embed=embed)

    @commands.group(name='set')
    async def set_(self, ctx):
        pass

    @set_.command(name='github_name', aliases=['githubname'])
    async def set_github_name(self, ctx, github_name):
        try:
            user = self.bot.github.get_user(github_name)
        except github.UnknownObjectException:
            return await ctx.send("Invalid github name")

        data = await self.bot.db.fetch('SELECT name FROM config WHERE user_id = $1 AND type = $2', ctx.author.id, 'github_name')
        if data:
            await self.bot.db.execute("UPDATE config SET name = $1 WHERE user_id = $2 AND type = $3", github_name, ctx.author.id, 'github_name')
        else:
            await self.bot.db.execute("INSERT INTO config (name, user_id, type) VALUES ($1, $2, $3)", github_name, ctx.author.id, 'github_name')
        await ctx.send("Done!")

    @set_.command(name='preferred_language', aliases=['preferredlanguage', 'preferred_lang','pl'])
    async def set_preferred_language(self, ctx, language):
        if language not in ['python', 'javascript']:
            return await ctx.send("Only python and javascript are supported")

        data = await self.bot.db.fetch('SELECT name FROM config WHERE user_id = $1 AND type = $2', ctx.author.id, 'preferred_language')
        if data:
            await self.bot.db.execute("UPDATE config SET name = $1 WHERE user_id = $2 AND type = $3", language, ctx.author.id, 'preferred_language')
        else:
            await self.bot.db.execute("INSERT INTO config (name, user_id, type) VALUES ($1, $2, $3)", language, ctx.author.id, 'preferred_language')
        await ctx.send("Done!")

async def setup(bot: commands.Bot):
    await bot.add_cog(Misc(bot))

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

        data = await self.bot.db.fetch('SELECT github_name FROM github_names WHERE user_id = $1', ctx.author.id)
        if data:
            await self.bot.db.execute("UPDATE github_names SET github_name = $1 WHERE user_id = $2", github_name, ctx.author.id)
        else:
            await self.bot.db.execute("INSERT INTO github_names (github_name, user_id) VALUES ($1, $2)", github_name, ctx.author.id)
        await ctx.send("Done!")

async def setup(bot: commands.Bot):
    await bot.add_cog(Misc(bot))

    

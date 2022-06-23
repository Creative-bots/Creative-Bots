import discord
from discord.ext import commands

from bot.helpers.embeds import Success, Error, ManagerEmbed as Embed


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        embed = Embed(
            title="Pong! 🏓",
            description=f"Current client latency: {self.bot.latency * 1000:.0f}ms",
            color=discord.Color.random()
        )

        embed.default_footer(ctx)

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Misc(bot))

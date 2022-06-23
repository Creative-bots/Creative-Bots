import discord
from discord.ext import commands

class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Pong! 🏓",
            description=f"Current client latency: {self.bot.latency*1000:.0f}ms",
            color=discord.Color.random()
        )
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Misc(bot))
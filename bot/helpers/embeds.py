import discord
from discord.ext import commands


class ManagerEmbed(discord.Embed):
    def default_footer(
            self,
            ctx: commands.Context,
            text: str = "Requested by {}",
    ) -> None:
        text = text.format(ctx.author)

        if av := ctx.author.avatar:
            self.set_footer(text=text, icon_url=av.url)
        else:
            self.set_footer(text=text)


class Success(ManagerEmbed):
    def __init__(self, title: str, description: str):
        super().__init__(title="✅ " + title, description=description, color=discord.Color.green())


class Error(ManagerEmbed):
    def __init__(self, title: str, description: str):
        super().__init__(title="❌ " + title, description=description, color=discord.Color.red())

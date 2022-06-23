from __future__ import annotations

import random
import string

import discord
from discord.ext import commands
import typing
from bot.helpers.embeds import Success, Error, ManagerEmbed as Embed

if typing.TYPE_CHECKING:
    from ..main import Manager


class Dev(commands.Cog):
    def __init__(self, bot: Manager) -> None:
        self.bot: Manager = bot

    async def cog_check(self, ctx):
        role = ctx.guild.get_role(988221429608767499)
        return (await self.bot.is_owner(ctx.author)) or role in ctx.author.roles

    @commands.group(name='idea')
    async def idea_(self, ctx):
        pass

    @idea_.command(name='create')
    async def idea_create(self, ctx, *, idea):
        idea_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
        dev_category = self.bot.dev_category

        role = await ctx.guild.create_role(name=idea_code)
        await ctx.author.add_roles(role)

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True)
        }
        channel = await dev_category.create_text_channel(idea, topic=ctx.author.id, overwrites=overwrites)

        success_embed = Success(
            title=f"Idea Successfully Created",
            description=f"{channel.mention} has been created for your idea."
        )

        success_embed.default_footer(ctx)

        await ctx.send(embed=success_embed)
        idea_embed = Embed(
            title=f"Idea \"{idea}\""
        )
        idea_embed.add_field(
            name="Idea Code:",
            value=f"`{idea_code}`"
        )

        idea_embed.default_footer(ctx, text="Idea created by {}")

        await channel.send(embed=idea_embed)

    @idea_.command(name='join')
    async def idea_join(self, ctx, idea_code) -> discord.Message | None:
        role = discord.utils.get(ctx.guild.roles, name=idea_code)

        if role in ctx.author.roles:
            embed = Error(title="Failed to Join Idea", description=f"You are already in idea `{role.name}`")
            return await ctx.send(embed=embed)

        await ctx.author.add_roles(role)

        embed = Success(title="Idea Joined", description=f"You have successfully joined idea `{role.name}`.")

        embed.default_footer(ctx)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Dev(bot))

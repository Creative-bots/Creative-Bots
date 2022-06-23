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

    @idea_.command(name='suggest')
    async def idea_suggest(self, ctx, idea_name, *, idea):
        idea_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
        idea_channel = self.bot.get_channel(988221597586440212)

        embed = Embed(title=idea_name, description=idea)
        embed.add_field(name='Idea code:', value=f"`{idea_code}`")
        embed.default_footer(ctx)

        msg = await idea_channel.send(embed=embed)

        await self.bot.db.execute('INSERT INTO ideas(idea, idea_name, idea_code, idea_message_id) VALUES ($1, $2, $3, $4)', idea, idea_name, idea_code, msg.id)

    @idea_.command('approve')
    async def idea_approve(self, ctx, idea_code):
        data = await self.bot.db.fetch("SELECT idea_message_id, idea_name, idea FROM ideas WHERE idea_code = $1", idea_code)
        if not data:
            return await ctx.send('No idea with that code found.')

        dev_category = self.bot.dev_category
        idea_channel = self.bot.get_channel(988221597586440212)
        msg = await idea_channel.fetch_message(data[0].get('idea_message_id'))
        if not msg:
            await self.bot.db.execute('DELETE FROM ideas WHERE idea_code = $1', idea_code)
            return await ctx.send("No idea with that code found.")

        await self.bot.db.execute("UPDATE ideas SET status = $1 WHERE idea_code = $2", "approved", idea_code)

        embed = Success(title=data[0].get('idea_name'), description=data[0].get('idea'))
        embed.add_field(name='Idea code:', value=f"`{idea_code}`")
        embed.default_footer(ctx, text='Approved by {}')
        await msg.edit(embed=embed)

        await ctx.send("Approved idea\n"+msg.jump_url)

    @idea_.command('deny')
    async def idea_deny(self, ctx, idea_code):
        data = await self.bot.db.fetch("SELECT idea_message_id, idea_name, idea FROM ideas WHERE idea_code = $1", idea_code)
        if not data:
            return await ctx.send('No idea with that code found.')

        dev_category = self.bot.dev_category
        idea_channel = self.bot.get_channel(988221597586440212)
        msg = await idea_channel.fetch_message(data[0].get('idea_message_id'))
        if not msg:
            await self.bot.db.execute('DELETE FROM ideas WHERE idea_code = $1', idea_code)
            return await ctx.send("No idea with that code found.")

        await self.bot.db.execute("UPDATE ideas SET status = $1 WHERE idea_code = $2", "denied", idea_code)

        embed = Error(title=data[0].get('idea_name'), description=data[0].get('idea'))
        embed.add_field(name='Idea code:', value=f"`{idea_code}`")
        embed.default_footer(ctx, text='Denied by {}')
        await msg.edit(embed=embed)

        await ctx.send("Denied idea\n"+msg.jump_url)

    @idea_.command(name='create')
    async def idea_create(self, ctx, idea_code):
        data = await self.bot.db.fetch("SELECT idea_name, idea, status, idea_message_id FROM ideas WHERE idea_code = $1", idea_code)
        if not data:
            return await ctx.send('No idea with that code found.')

        dev_category = self.bot.dev_category
        idea_channel = self.bot.get_channel(988221597586440212)
        msg = await idea_channel.fetch_message(data[0].get('idea_message_id'))
        if not msg:
            await self.bot.db.execute('DELETE FROM ideas WHERE idea_code = $1', idea_code)
            return await ctx.send("No idea with that code found.")

        idea_name = data[0].get('idea_name')
        idea = data[0].get('idea')
        status = data[0].get('status')
        if status == 'made':
            return await ctx.send(f"Idea with code (`{idea_code}`) has already been created")
        elif status != 'approved':
            return await ctx.send(f"Idea with code (`{idea_code}`) is not approved")

        role = await ctx.guild.create_role(name=idea_name)
        await ctx.author.add_roles(role)

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True)
        }

        channel = await dev_category.create_text_channel(idea_name, topic=idea_code, overwrites=overwrites)

        success_embed = Success(
            title=f"Idea Successfully Created",
            description=f"{channel.mention} has been created for your idea."
        )

        success_embed.default_footer(ctx)

        await ctx.send(embed=success_embed)
        idea_embed = Embed(
            title=f"Idea \"{idea_name}\"",
            description=idea
        )
        idea_embed.add_field(
            name="Idea Code:",
            value=f"`{idea_code}`"
        )

        idea_embed.default_footer(ctx, text="Idea created by {}")

        await channel.send(embed=idea_embed)

        await self.bot.db.execute("UPDATE ideas SET status = $1 AND idea_owner_id = $2 WHERE idea_code = $3", "made", ctx.author.id, idea_code)

    @idea_.command(name='join')
    async def idea_join(self, ctx, member: discord.Member, idea_code) -> discord.Message | None:

        data = await self.bot.db.fetch("SELECT idea_owner_id, idea_name, status FROM ideas WHERE idea_code = $1", idea_code)
        if not data:
            return await ctx.send('No idea with that code found.')

        idea_owner_id = data[0].get('idea_owner_id')
        idea_name = data[0].get('idea_name')
        status = data[0].get('status')
        if not ((await self.bot.is_owner(ctx.author)) or ctx.author.id == idea_owner_id):
            return await ctx.send(f"You don't have permission to join people into idea with code (`{idea_code}`)")
        elif status != 'made':
            return await ctx.send("Idea has not been created yet")

        role = discord.utils.get(ctx.guild.roles, name=idea_name)

        if role in member.roles:
            embed = Error(title="Failed to Join Idea", description=f"{member.mention} is already in idea with code (`{idea_code}`)")
            return await ctx.send(embed=embed)

        await ctx.author.add_roles(role)

        embed = Success(title="Idea Joined", description=f"{member.mention} has successfully joined idea with code (`{idea_code}`)")
        embed.default_footer(ctx)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Dev(bot))

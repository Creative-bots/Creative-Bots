from __future__ import annotations

import random
import string

import discord
from discord.ext import commands
import typing
import json
import os
from bot.helpers.embeds import Success, Error, ManagerEmbed as Embed

if typing.TYPE_CHECKING:
    from ..main import Manager


class Dev(commands.Cog):
    def __init__(self, bot: Manager) -> None:
        self.bot: Manager = bot

    async def cog_check(self, ctx):
        role = ctx.guild.get_role(988221429608767499)
        return (await self.bot.is_owner(ctx.author)) or role in ctx.author.roles

    @commands.group(name='idea', invoke_without_command=True)
    async def idea_(self, ctx):
        await ctx.send_help('idea')

    @idea_.command(name='suggest')
    async def idea_suggest(self, ctx, idea_name, *, idea):
        idea_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
        idea_channel = self.bot.get_channel(988221597586440212)

        embed = Embed(title=idea_name, description=idea)
        embed.add_field(name='Idea code:', value=f"`{idea_code}`")
        embed.default_footer(ctx)

        msg = await idea_channel.send(embed=embed)

        await self.bot.db.execute('INSERT INTO ideas(idea, idea_name, idea_code, idea_message_id, status) VALUES ($1, $2, $3, $4, $5)', idea, idea_name, idea_code, msg.id, "waiting")

    @idea_.command('approve')
    @commands.is_owner()
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
    @commands.is_owner()
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

        with open(os.path.join('bot', 'template_repo.json'), "r") as f:
            repo_template = json.load(f)

        org = self.bot.github.get_organization("Creative-bots")
        repo = org.create_repo(idea_name)
        for file_name, file_content in repo_template['python'].items():
            file_content = file_content.replace(r'\n','\n').replace(r'\t', '    ')
            if file_name == 'README.md':
                file_content = file_content.format(idea_name, idea)
            repo.create_file(file_name, 'main commit', file_content, branch='main')


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
        await channel.send(f"https://github.com/Creative-bots/{idea_name.replace(' ', '-')}")

        await self.bot.db.execute("UPDATE ideas SET status = $1 WHERE idea_code = $2", "made", idea_code)
        await self.bot.db.execute("UPDATE ideas SET idea_owner_id = $1 WHERE idea_code = $2", ctx.author.id, idea_code)

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

        await member.add_roles(role)

        embed = Success(title="Idea Joined", description=f"{member.mention} has successfully joined idea with code (`{idea_code}`)")
        embed.default_footer(ctx)
        await ctx.send(embed=embed)

    @idea_.command(name='close')
    async def idea_close(self, ctx, idea_code):
        data = await self.bot.db.fetch("SELECT idea_name, status FROM ideas WHERE idea_code = $1", idea_code)
        if not data:
            return await ctx.send('No idea with that code found.')

        idea_name = data[0].get('idea_name')
        role = discord.utils.get(ctx.guild.roles, name=idea_name)

        idea_name = ('-'.join(idea_name.split())).lower()
        channel = discord.utils.get(ctx.guild.text_channels, name=idea_name)

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True),
            role: discord.PermissionOverwrite(send_messages=False),
        }

        await channel.edit(overwrites=overwrites, category=self.bot.archive_category)

        success_embed = Success(
            title=f"Idea Successfully Closed",
            description=f"{channel.mention} has been closed."
        )

        success_embed.default_footer(ctx)

        await ctx.send(embed=success_embed)

    @idea_.command(name='open')
    async def idea_open(self, ctx, idea_code):
        data = await self.bot.db.fetch("SELECT idea_name, status FROM ideas WHERE idea_code = $1", idea_code)
        if not data:
            return await ctx.send('No idea with that code found.')

        idea_name = data[0].get('idea_name')
        role = discord.utils.get(ctx.guild.roles, name=idea_name)

        idea_name = ('-'.join(idea_name.split())).lower()
        channel = discord.utils.get(ctx.guild.text_channels, name=idea_name)

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True),
            role: discord.PermissionOverwrite(send_messages=True),
        }

        await channel.edit(overwrites=overwrites, category=self.bot.dev_category)

        success_embed = Success(
            title=f"Idea Successfully Opened",
            description=f"{channel.mention} has been opened."
        )

        success_embed.default_footer(ctx)

        await ctx.send(embed=success_embed)

async def setup(bot):
    await bot.add_cog(Dev(bot))

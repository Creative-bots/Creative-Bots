import discord
import random
import string
from discord.ext import commands

class Dev(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		role = ctx.guild.get_role(988221429608767499)
		return (await self.bot.is_owner(ctx.author)) or role in ctx.author.roles

	@commands.group(name='idea')
	async def idea_(self, ctx):
		pass

	@idea_.command(name='create')
	async def idea_create(self, ctx, *, idea):

		idea_code = ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(10))
		dev_category = ctx.guild.get_channel(988221364886462486)

		role = await ctx.guild.create_role(name=idea_code)
		await ctx.author.add_roles(role)

		overwrites = {
			ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
			role: discord.PermissionOverwrite(read_messages=True)
		}
		channel = await dev_category.create_text_channel(idea, topic=ctx.author.id, overwrites=overwrites)

		await ctx.send(f"{channel.mention} has been created for you")
		await channel.send(f"Idea: {idea}\nIdea code: `{idea_code}`\nIdea creator: {ctx.author.mention}")

async def setup(bot):
	await bot.add_cog(Dev(bot))
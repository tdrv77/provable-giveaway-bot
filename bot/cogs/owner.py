import traceback
import discord
from discord.ext import commands
from django.conf import settings


class OwnerCommands:
    """Owner-only cogs that make the bot dynamic."""

    def __init__(self, bot):
        self.bot = bot
        self.path = 'bot.cogs.'

    @commands.command(hidden=True)
    async def load(self, ctx, *, module):
        """Loads a module."""
        self.bot.load_extension(f'{self.path}{module}')
        await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        self.bot.unload_extension(f'{self.path}{module}')
        await ctx.send('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    async def _reload(self, ctx, *, module):
        """Reloads a module."""

        self.bot.unload_extension(f'{self.path}{module}')
        self.bot.load_extension(f'{self.path}{module}')
        await ctx.send('\N{OK HAND SIGN}')

    @load.error
    @unload.error
    @_reload.error
    async def _error_handler(self, context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await context.say_as_embed(
                f'The command **{context.invoked_with}** is missing a required argument: `module`',
                color='error')


def setup(bot):
    bot.add_cog(OwnerCommands(bot))

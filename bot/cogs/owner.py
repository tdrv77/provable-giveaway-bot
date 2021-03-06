from discord.ext import commands


class OwnerCommands(commands.Cog):
    """Owner-only commands that make the bot dynamic."""

    def __init__(self, bot):
        self.bot = bot
        self.__cog_name__ = 'Owner Commands'
        self.path = 'bot.cogs.'
        self.path2 = 'bot.tasks.'

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, context, *, module):
        """Loads a module."""
        try:
            self.bot.load_extension(f'{self.path}{module}')
        except commands.ExtensionError:
            self.bot.load_extension(f'{self.path2}{module}')

        await context.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, context, *, module):
        """Unloads a module."""
        try:
            self.bot.unload_extension(f'{self.path}{module}')
        except commands.ExtensionError:
            self.bot.unload_extension(f'{self.path2}{module}')

        await context.send('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _reload(self, context, *, module):
        """Reloads a module."""

        try:
            self.bot.unload_extension(f'{self.path}{module}')
            self.bot.load_extension(f'{self.path}{module}')
        except commands.ExtensionError:
            self.bot.unload_extension(f'{self.path2}{module}')
            self.bot.load_extension(f'{self.path2}{module}')

        await context.send('\N{OK HAND SIGN}')

    @load.error
    @unload.error
    @_reload.error
    async def _error_handler(self, context, error):
        pass


def setup(bot):
    bot.add_cog(OwnerCommands(bot))

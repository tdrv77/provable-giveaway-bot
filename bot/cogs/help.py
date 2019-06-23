import discord
from discord.ext import commands
from .helptexts import _help

class HelpCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.__cog_name__ = 'Help Commands'

    @commands.command(name='help', help=_help)
    async def _help_message(self, context, command_name: str):

        command_obj = discord.utils.get(context.bot.commands, name=command_name)
        if not command_obj:
            command_obj = discord.utils.get(context.bot.commands, aliases=[command_name])

        if not command_obj:
            await context.say_as_embed(
                f'There are no commands named `{command_name}`.', color='error')
            return

        await context.say_as_embed(
            f'```{context.prefix}{command_obj.qualified_name} {command_obj.signature}```\n'
            f'{command_obj.help}'
        )

    @_help_message.error
    async def _error_handler(self, context, error):

        if isinstance(error, commands.MissingRequiredArgument):

            available_commands_txt = ''
            for cog_name, cog in context.bot.cogs.items():

                cog_commands_txt = ''
                for c in cog.get_commands():
                    if c.hidden:
                        continue
                    command_brief = c.help.split("\n")[0] if c.help else '-'
                    cog_commands_txt += f'• {c.qualified_name:<8} : {command_brief}\n'
                if cog_commands_txt:
                    available_commands_txt += f'{cog.qualified_name}\n{cog_commands_txt}\n'

            await context.say_as_embed(
                title='List of available commands',
                description=
                f'Prefix: `{context.prefix}`\n'
                f'```\n{available_commands_txt}```\n'
                f'Type `{context.prefix}{context.invoked_with} [command name]`'
                f' for more details on the command.',
                color='info')


def setup(bot):
    bot.add_cog(HelpCommands(bot))

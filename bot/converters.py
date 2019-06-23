from discord.ext import commands


class PositiveNumberConverter(commands.Converter):
    async def convert(self, context, argument):
        try:
            argument = int(argument)
        except ValueError:
            raise commands.BadArgument(f'`{argument}` is not a NUMBER.')

        if argument <= 0:
            raise commands.BadArgument(f'`{argument}` is not a POSITIVE number.')

        return argument

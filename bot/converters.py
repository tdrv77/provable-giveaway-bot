from discord.ext import commands
from db.apps.giveaways.models import Giveaway


class PositiveNumberConverter(commands.Converter):
    async def convert(self, context, argument):
        try:
            argument = int(argument)
        except ValueError:
            raise commands.BadArgument(f'`{argument}` is not a NUMBER.')

        if argument <= 0:
            raise commands.BadArgument(f'`{argument}` is not a POSITIVE number.')

        return argument


class OwnedGiveawayConverted(commands.Converter):
    async def convert(self, context, argument):
        argument = await PositiveNumberConverter().convert(context, argument)

        try:
            ga_obj = Giveaway.objects.get(
                creator__discord_id=context.author.id,
                id=argument,
            )
        except Giveaway.DoesNotExist:
            raise commands.BadArgument(f'Giveaway with ID `{argument}` does not exist, or you are not its creator.')

        return ga_obj

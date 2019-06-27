from discord.ext import commands, tasks
from django.conf import settings

from db.apps.giveaways.models import Giveaway


class UpdateGiveawayTimeRemaining(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.update_giveaway_time_remaining.start()

    def cog_unload(self):
        self.update_giveaway_time_remaining.cancel()

    @tasks.loop(seconds=settings.UPDATE_GIVEAWAY_REMAINING_TIME_DELAY if not settings.DEBUG else 5, reconnect=False)
    async def update_giveaway_time_remaining(self):
        ga_objs = Giveaway.objects.filter(success=None)

        if not ga_objs.exists():
            return

        for ga_obj in ga_objs:
            ga_obj.bot = self.bot
            await ga_obj.end(for_task=True)

    @update_giveaway_time_remaining.before_loop
    async def before_execute_timed_events_task(self):
        print('[Update Giveaway Time Remaining] Waiting for ready state...')

        await self.bot.wait_until_ready()

        print('[Update Giveaway Time Remaining] Ready and running!')


def setup(bot):
    bot.add_cog(UpdateGiveawayTimeRemaining(bot))

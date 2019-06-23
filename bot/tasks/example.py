import discord

from discord.ext import commands, tasks
from django.conf import settings


class ExampleTask(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.example_task.start()

    def cog_unload(self):
        self.example_task.cancel()

    @tasks.loop(seconds=settings.TIMED_EVENT_DELAY if not settings.DEBUG else 5)
    async def example_task(self):
        pass

    @example_task.before_loop
    async def before_execute_timed_events_task(self):
        print('[example_task] Waiting for ready state...')

        await self.bot.wait_until_ready()

        print('[example_task] Ready and running!')

def setup(bot):
    bot.add_cog(ExampleTask(bot))
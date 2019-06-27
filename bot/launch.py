import traceback
from bot.bot import CustomBot
from django.conf import settings


def launcher():
    bot = CustomBot()

    # Initialize extensions
    initial_extensions = (
        'bot.cogs.giveaway',
        'bot.cogs.help',
        'bot.cogs.owner',
        'bot.cogs.pfair',

        'bot.tasks.giveawaytask',

    )
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception:
            traceback.print_exc()

    bot.run(settings.BOT_TOKEN)

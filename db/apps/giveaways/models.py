import discord
from discord.ext import commands
from django.db import models
from django.utils import timezone

from db.apps.users.models import DiscordUser


class Giveaway(models.Model):
    creator = models.ForeignKey(DiscordUser, related_name='giveaways', on_delete=models.CASCADE)
    prize = models.CharField(max_length=200)
    winner_count = models.SmallIntegerField()
    participants = models.ManyToManyField(DiscordUser, related_name='+', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField()
    winners = models.ManyToManyField(DiscordUser, related_name='+', blank=True, null=True)
    success = models.BooleanField(
        null=True,
        help_text=
        '• Checked: Giveaway happened successfully.<br/>'
        '• Unchecked: Giveaway failed due to a Discord exception.<br/>'
        '• None: Giveaway happening.'
    )

    # Discord stuff
    channel_id = models.BigIntegerField()
    message_id = models.BigIntegerField()
    bot = None

    def __str__(self):
        return f'{self.prize} [{"Ended" if self.ended else "On going"}]'

    @property
    def ended(self):
        return timezone.now() > self.ended_at

    @property
    def discord_channel(self):
        if not isinstance(self.bot, discord.Client):
            raise AttributeError('`bot` must be `discord.Client`.')
        return self.bot.get_channel(self.channel_id)

    @property
    def discord_message(self):
        if not self.discord_channel:
            return None

        try:
            message = self.discord_channel.fetch_message(self.message_id)
        except discord.HTTPException:
            return None

        return message

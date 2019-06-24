import discord
from discord.ext import commands
from django.db import models
from django.utils import timezone

from db.apps.guilds.models import DiscordGuild
from db.apps.users.models import DiscordUser

from utils.time import process_elapsed_time_text


class Giveaway(models.Model):
    creator = models.ForeignKey(DiscordUser, related_name='giveaways', on_delete=models.CASCADE)
    prize = models.CharField(max_length=200)
    winner_count = models.SmallIntegerField()
    participants = models.ManyToManyField(DiscordUser, related_name='+', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField()
    ended_time_str = models.CharField(max_length=200)
    winners = models.ManyToManyField(DiscordUser, related_name='+', blank=True)
    success = models.BooleanField(
        null=True,
        help_text=
        '• Checked: Giveaway happened successfully.<br/>'
        '• Unchecked: Giveaway failed due to a Discord exception.<br/>'
        '• None: Giveaway happening.'
    )

    # Discord stuff
    guild = models.ForeignKey(DiscordGuild, related_name='giveaways', on_delete=models.CASCADE)
    channel_id = models.BigIntegerField(blank=True, null=True)
    message_id = models.BigIntegerField(blank=True, null=True)
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

    @property
    def message_jump_url(self):
        if self.guild and self.channel_id and self.message_id:
            return f'https://discordapp.com/channels/{self.guild.guild_id}/{self.channel_id}/{self.message_id}'
        else:
            return None

    @property
    def ga_embed(self):
        embed = discord.Embed(
            title='Result Provable Giveaway',
            description=
            f'• Prize: **{self.prize}**\n'
            f'• Winners: **{self.winner_count}**\n'
            f'• Time remaining: **{self.time_remaining}**\n\n'
            f'React with [emoji] to enter!',
            timestamp=self.ended_at.astimezone(timezone.utc)
        )
        embed.set_footer(text='Ends at')

        return embed

    @property
    def time_remaining(self):
        if not self.ended:
            return process_elapsed_time_text(self.ended_at - timezone.now())
        else:
            return 'Ended'

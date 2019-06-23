from django.db import models


class DiscordGuild(models.Model):
    guild_id = models.BigIntegerField()
    name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

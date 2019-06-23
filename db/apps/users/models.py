from django.db import models
from django.utils import timezone
from utils.core import generate_server_seed


class DiscordUser(models.Model):
    discord_id = models.BigIntegerField()
    name = models.CharField(max_length=200, blank=True)
    discriminator = models.CharField(max_length=4)
    logged_at = models.DateTimeField(auto_now_add=True)

    # provable fairness information
    user_seed = models.CharField(max_length=200)
    server_seed = models.CharField(max_length=300)

    def __str__(self):
        return f'{self.name}#{self.discriminator}'

    def clean(self):
        if not self.user_seed:
            self.user_seed = self.discord_id

        self.server_seed = generate_server_seed()

        super().clean()

    @property
    def has_ongoing_giveaways(self):
        return self.giveaways.filter(ended_at__gt=timezone.now()).exists()

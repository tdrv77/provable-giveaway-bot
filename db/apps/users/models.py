import hashlib
import hmac

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
    nonce = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.name}#{self.discriminator}'

    def save(self, **kwargs):
        if not self.user_seed:
            self.user_seed = self.discord_id
        if not self.server_seed:
            self.server_seed = generate_server_seed()

        super().save(**kwargs)

    @property
    def has_ongoing_giveaways(self):
        return self.giveaways.filter(ended_at__gt=timezone.now()).exists()

    @property
    def server_seed_hashed(self):
        if self.server_seed:
            return hashlib.sha512(self.server_seed.encode()).hexdigest()
        return None

    def pfair_randomize(self, index):

        HMAC = hmac.new(
            self.server_seed.encode(),
            f'{self.user_seed}-{self.nonce}'.encode(),
            'sha512'
        )
        hmac_str = HMAC.hexdigest()
        to_decimal = int(hmac_str[:5], 16)

        result = to_decimal % index

        self.nonce += 1
        self.save()

        return result, self.nonce - 1


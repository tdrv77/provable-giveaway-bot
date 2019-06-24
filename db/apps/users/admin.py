from django.contrib import admin
from .models import DiscordUser


class DiscordUserAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'discriminator',
        'discord_id'
    )


admin.site.register(DiscordUser, DiscordUserAdmin)

admin.site.site_header = 'Provable Giveaway Bot Admin Panel'
admin.site.site_title = 'Provable Giveaway Bot Admin Panel'

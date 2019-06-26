from django.contrib import admin
from .models import Giveaway, Winner


class GiveawayAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'creator',
        'prize',
        'winner_count',
        'status',
        'created_at',
        'ending_at',
        'ended_time_str',
        'success',
        'guild',
    )

class WinnerAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'giveaway',
        'index',
        'nonce',
    )

admin.site.register(Winner, WinnerAdmin)
admin.site.register(Giveaway, GiveawayAdmin)

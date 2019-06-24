from db.apps.guilds.models import DiscordGuild
from db.apps.users.models import DiscordUser


def get_user_obj(discord_user):
    user_obj, created = DiscordUser.objects.update_or_create(
        discord_id=discord_user.id,
        defaults={
            'discriminator': discord_user.discriminator,
            'name': discord_user.name
        }
    )
    return user_obj, created


def get_guild_obj(discord_guild):
    guild_obj, created = DiscordGuild.objects.get_or_create(
        guild_id=discord_guild.id,
        defaults={
            'name': discord_guild.name
        }
    )

    return guild_obj, created

# from db.apps.users.models import DiscordUser
#
#
# def get_user_obj(discord_user):
#     user_obj, created = DiscordUser.objects.update_or_create(
#         discord_id=discord_user.id,
#         defaults={
#             'discriminator': discord_user.discriminator,
#             'discord_name': discord_user.display_name
#         }
#     )
#     return user_obj

import random
import string


def generate_server_seed():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=300))

import io
import traceback

import dateparser as dateparser
import discord
from datetime import datetime, timezone
from discord.ext import commands
from django.conf import settings

from db.apps.giveaways.models import Giveaway
from .helptexts import (
    _ga_create_brief, _ga_create_help,
    _ga_end_brief, _ga_end_help,
    _ga_reroll_brief, _ga_reroll_help,
    _ga_delete_brief, _ga_delete_help,
    _ga_result_brief, _ga_result_help,
)
from utils.objects import get_user_obj, get_guild_obj
from bot.validators import validate_input
from bot.converters import OwnedGiveawayConverted


class MissingManageGuildPermissionAndGiveawayRole(commands.CheckFailure):
    def __init__(self, message=None):
        super().__init__(
            message or 'You must have either **Manage Server** permission or '
                       '**Giveaway** role to use this command.')


async def manage_guild_or_giveaway_role(context):
    permissions = context.channel.permissions_for(context.author)

    if permissions.manage_guild:
        return True

    role = discord.utils.get(context.author.roles, name='Giveaway')
    if role:
        return True

    raise MissingManageGuildPermissionAndGiveawayRole()


class GiveawayCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.__cog_name__ = 'Giveaway Commands'

    @commands.command(name='create', brief=_ga_create_brief, help=_ga_create_help)
    @commands.guild_only()
    @commands.check(manage_guild_or_giveaway_role)
    async def _interactive_setup(self, context):

        user_obj, _ = get_user_obj(context.author)
        guild_obj, _ = get_guild_obj(context.guild)

        ga_data = {
            'creator': user_obj,
            'guild': guild_obj,
        }

        # step 1/4: Ask for prize name
        await context.say_as_embed(
            title='What is the **prize** for this giveaway? (Max: 200 characters)',
        )

        response = await validate_input(context, inputs=None, max_length=200)
        if response is False:
            return

        ga_data['prize'] = response.content

        # step 2/4: Ask for number of winners
        await context.say_as_embed(
            title='How many winners are there for this giveaway? (Max: 20 winners)'
        )

        response = await validate_input(context, inputs=[str(n) for n in range(1, 21)])
        if response is False:
            return

        ga_data['winner_count'] = int(response.content)

        # step 3/4: Ask for end date time of the giveaway
        await context.say_as_embed(
            title='When will this giveaway end?',
            description=
            'Enter as you want and I will try to understand you.\n'
            'Default Timezone (when not specified): `UTC`\n\n'
            'Example:\n'
            '• in 10 hours and 30 minutes\n'
            '• 10AM June 24th, 2019 PDT'
        )

        while True:

            response = await validate_input(context, inputs=None)
            if response is False:
                return

            async with context.channel.typing():
                parsed_dt = dateparser.parse(response.content, settings={'RETURN_AS_TIMEZONE_AWARE': True})

            if not parsed_dt:
                await context.say_as_embed(
                    'Unable to convert the date time provided. Please enter again.',
                    delete_after=5, color='error')
                continue

            if parsed_dt < datetime.now(timezone.utc):
                await context.say_as_embed(
                    'The time you entered is already in the past! Please try again.\n'
                    f'Time entered: `{parsed_dt:%H:%M:%S %A %B %d, %Y (%Z)}`',
                    delete_after=5 * 2, color='error')
                continue

            ga_data['ending_at'] = parsed_dt
            ga_data['ended_time_str'] = f'{parsed_dt:%H:%M:%S %A %B %d, %Y (%Z)}'
            break

        # step 4/4: Ask for a channel to post the giveaway message
        await context.say_as_embed(
            title='Finally, where should the giveaway message be posted?'
        )

        text_channel_converter = commands.TextChannelConverter()
        ga_channel = None
        while True:
            response = await validate_input(context, inputs=None)
            if response is False:
                return

            try:
                channel = await text_channel_converter.convert(context, response.content)
            except commands.BadArgument as e:
                await context.say_as_embed(f'{str(e)} Please try again.', delete_after=5, color='error')
                continue

            if channel.guild != context.guild:
                await context.say_as_embed(
                    'The channel must be in this server! Please try again.', delete_after=5, color='error'
                )
                continue

            bot_member = context.guild.get_member(context.bot.user.id)
            if not bot_member:
                print(f'Bot is not a member of guild {context.guild.name} (ID: {context.guild.id}).')
                return

            perms = channel.permissions_for(bot_member)
            if perms.send_messages is False or perms.add_reactions is False:
                await context.say_as_embed(
                    f'I can\'t send messages or add reactions (missing permissions) in {channel.mention}! '
                    f'Please try again.',
                    delete_after=5, color='error'
                )
                continue

            ga_channel = channel
            ga_data['channel_id'] = channel.id

            break

        if not ga_channel:
            return

        # finally, ask for information confirmation
        embed = discord.Embed(
            title='Giveaway Creation Confirmation',
            description=
            'Below is the Giveaway info you entered:\n'
            f'• Prize: **{ga_data["prize"]}**\n'
            f'• Winners: **{ga_data["winner_count"]}**\n'
            f'• End at: **{ga_data["ended_time_str"]}**\n'
            f'• Channel: {ga_channel.mention}\n',
            color=settings.EMBED_DEFAULT_COLOR
        )
        embed.add_field(
            name='Proceed to creation?',
            value='Y/N'
        )

        await context.send(embed=embed)

        response = await validate_input(context, inputs=['y', 'yes', 'n', 'no'])
        if response is False:
            return

        # create the giveaway based on collected user inputs
        ga_obj = Giveaway.objects.create(**ga_data)

        # send the giveaway embedded message
        try:
            ga_message = await ga_channel.send(embed=ga_obj.embed)
        except discord.HTTPException:
            ga_obj.delete()
            await context.say_as_embed('Sending message failed. Please try again.', color='error')
            return

        # get the message ID and save to database
        ga_obj.message_id = ga_message.id
        ga_obj.save()

        # get the emoji
        emoji = self.bot.get_emoji(settings.REACT_EMOJI_ID)
        if not emoji:
            ga_obj.delete()
            await context.say_as_embed(f'Emoji with ID {settings.REACT_EMOJI_ID} does not exist.', color='error')
            return

        # try to react with the customized emoji
        try:
            await ga_message.add_reaction(emoji)
        except discord.HTTPException:
            ga_obj.delete()
            await context.say_as_embed(f'Reacting with emoji {str(emoji)} failed.', color='error')
            return

        # after all those checks, it's finally here, phew!
        await context.say_as_embed(
            title='Giveaway Created!',
            description=
            f'You can [click here]({ga_obj.message_jump_url}) to go to the Giveaway message.\n'
            f'Giveaway ID: `{ga_obj.id}`',
            color='success'
        )

    @commands.command(name='end', brief=_ga_end_brief, help=_ga_end_help)
    @commands.guild_only()
    @commands.check(manage_guild_or_giveaway_role)
    async def _end_giveaway(self, context, ga_obj: OwnedGiveawayConverted):

        ga_obj.bot = self.bot
        await ga_obj.end(context=context)

    @commands.command(name='reroll', brief=_ga_reroll_brief, help=_ga_reroll_help)
    @commands.guild_only()
    @commands.check(manage_guild_or_giveaway_role)
    async def _reroll_giveaway(self, context, ga_obj: OwnedGiveawayConverted):

        ga_obj.bot = self.bot
        await ga_obj.end(for_reroll=True, context=context)

    @commands.command(name='delete', brief=_ga_delete_brief, help=_ga_delete_help)
    @commands.guild_only()
    @commands.check(manage_guild_or_giveaway_role)
    async def _delete_giveaway(self, context, ga_obj: OwnedGiveawayConverted):

        await context.say_as_embed(
            title='You are about to delete your Giveaway',
            description=
            f'• ID: `{ga_obj.id}`\n'
            f'• Prize: **{ga_obj.prize}**\n'
            f'• Winners: **{ga_obj.winner_count}**\n'
            f'• Time remaining: **{ga_obj.time_remaining}**\n\n'
            f'**Proceed to deletion?**\n'
            f'Y/N'
        )

        response = await validate_input(context, inputs=['y', 'yes', 'n', 'no'])
        if response is False:
            return

        # tries to delete the giveaway message
        ga_obj.bot = self.bot
        discord_message = await ga_obj.discord_message()
        if discord_message:
            try:
                await discord_message.delete()
            except discord.HTTPException:
                pass

        # collects the GA ID before deleting it
        ga_obj_id = ga_obj.id

        # deletes the GA object from database
        ga_obj.delete()

        await context.say_as_embed(
            title=f'Giveaway ID [{ga_obj_id}] has been deleted',
            color='success'
        )

    @commands.command(name='result', brief=_ga_result_brief, help=_ga_result_help)
    @commands.guild_only()
    @commands.check(manage_guild_or_giveaway_role)
    @commands.bot_has_permissions(attach_files=True)
    async def _request_giveaway_result(self, context, ga_obj: OwnedGiveawayConverted):

        if not ga_obj.ended_at:
            await context.say_as_embed(
                f'{context.author.mention}, this Giveaway has not ended yet. '
                f'You can only retrieve results of ended giveaways.', color='warning'
            )
            return

        filename = f'GA{ga_obj.id}_{ga_obj.creator.discord_id}.txt'

        str_data = io.BytesIO(ga_obj.info_text.encode())
        await context.send(file=discord.File(str_data, filename))

    @_interactive_setup.error
    @_end_giveaway.error
    @_reroll_giveaway.error
    @_delete_giveaway.error
    @_request_giveaway_result.error
    async def _error_handler(self, context, error):
        if isinstance(error, MissingManageGuildPermissionAndGiveawayRole):
            await context.say_as_embed(str(error), color='error')


def setup(bot):
    bot.add_cog(GiveawayCommands(bot))

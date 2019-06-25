from pprint import pprint

import dateparser as dateparser
import discord
from datetime import datetime, timezone
from discord.ext import commands
from django.conf import settings

from db.apps.giveaways.models import Giveaway
from .helptexts import _ga_brief, _ga_help
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

    @commands.command(name='end', brief=_ga_brief, help=_ga_help)
    @commands.guild_only()
    @commands.check(manage_guild_or_giveaway_role)
    async def _end_giveaway(self, context, ga_obj: OwnedGiveawayConverted):

        ga_obj.bot = self.bot
        await ga_obj.end(context=context)

    @commands.command(name='reroll', brief=_ga_brief, help=_ga_help)
    @commands.guild_only()
    @commands.check(manage_guild_or_giveaway_role)
    async def _reroll_giveaway(self, context, ga_obj: OwnedGiveawayConverted):

        ga_obj.bot = self.bot
        await ga_obj.end(for_reroll=True, context=context)

    @commands.command(name='delete', brief=_ga_brief, help=_ga_help)
    @commands.guild_only()
    @commands.check(manage_guild_or_giveaway_role)
    async def _delete_giveaway(self, context, ga_obj: OwnedGiveawayConverted):

        await context.say_as_embed(
            title='You are about to delete your Giveaway',
            description=
            f'• ID: `{ga_obj.id}`\n'
            f'• Prize: **{ga_obj.prize}`\n'
            f'• Winners: **{ga_obj.winner_count}**\n'
            f'• Time remaining: **{ga_obj.time_remaining}**\n\n'
            f'**Proceed to deletion?**\n'
            f'Y/N'
        )

        response = validate_input(context, inputs=['y', 'yes', 'n', 'no'])
        if not response:
            return

        # tries to delete the giveaway message
        ga_obj.bot = self.bot
        discord_message = await ga_obj.discord_message()
        if discord_message:
            try:
                await discord_message.delete()
            except discord.HTTPException:
                pass

        await context.say_as_embed(
            title=f'Giveaway ID [{ga_obj.id}] has been deleted',
            color='success'
        )

    @commands.command(name='create', brief=_ga_brief, help=_ga_help)
    @commands.guild_only()
    @commands.check(manage_guild_or_giveaway_role)
    async def _interactive_setup(self, context):

        user_obj, created = get_user_obj(context.author)
        # if created:
        #     await self.send_pfair_info(context, user_obj)

        guild_obj, _ = get_guild_obj(context.guild)

        ga_data = {
            'creator': user_obj,
            'guild': guild_obj,
        }

        await context.say_as_embed(
            title='What is the **prize** for this giveaway? (Max: 200 characters)',
        )

        response = await validate_input(context, inputs=None, max_length=200)
        if response is None:
            return

        ga_data['prize'] = response.content

        await context.say_as_embed(
            title='How many winners are there for this giveaway? (Max: 20 winners)'
        )

        response = await validate_input(context, inputs=[str(n) for n in range(1, 21)])
        if response is None:
            return

        ga_data['winner_count'] = int(response.content)

        await context.say_as_embed(
            title='When will this giveaway end?',
            description=
            'Enter as you want and I will try to understand you.\n'
            'Default Timezone (when not specified): `UTC`\n\n'
            'Example:\n'
            '• in 10 hours\n'
            '• 10AM June 24th, 2019 PDT'
        )

        while True:

            response = await validate_input(context, inputs=None)
            if response is None:
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

            ga_data['ended_at'] = parsed_dt
            ga_data['ended_time_str'] = f'{parsed_dt:%H:%M:%S %A %B %d, %Y (%Z)}'
            break

        await context.say_as_embed(
            title='Finally, where should the giveaway message be posted?'
        )

        text_channel_converter = commands.TextChannelConverter()
        ga_channel = None
        while True:
            response = await validate_input(context, inputs=None)
            if response is None:
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
        if response is None:
            return

        if response.content.lower() not in ['y', 'yes']:
            return

        ga_obj = Giveaway.objects.create(**ga_data)

        try:
            ga_message = await ga_channel.send(embed=ga_obj.embed)
        except discord.HTTPException:
            return

        ga_obj.message_id = ga_message.id
        ga_obj.save()

        try:
            emoji = self.bot.get_emoji(settings.REACT_EMOJI_ID)
            if not emoji:
                print(f'Emoji with ID {settings.REACT_EMOJI_ID} does not exist.')
                return
            await ga_message.add_reaction(emoji)
        except discord.HTTPException:
            return

        await context.say_as_embed(
            title='Giveaway Created!',
            description=
            f'You can [click here]({ga_obj.message_jump_url}) to go to the Giveaway message.',
            color='success'
        )

    async def send_pfair_info(self, context, user_obj):
        embed = discord.Embed(
            title='New User Provable Fairness Information',
            description=
            f'Hello {context.author.mention}! This is the first time you created a Giveaway with me, '
            f'so here is your Provable Fairness Information:\n```\n'
            f'• User Seed: {user_obj.user_seed}\n'
            f'• Server Seed (hashed): {user_obj.server_seed_hashed}\n'
            f'• Nonce: {user_obj.nonce}\n'
            f'```',
            color=settings.EMBED_DEFAULT_COLOR
        )
        embed.add_field(
            name='Please Don\'t Freak Out!',
            value=
            '**You can just ditch those information and proceed with the Giveaway creation**. '
            'The info is good when someone goes salty and wants to check the result generated by my '
            '**Randomization Algorithm** to pick the winners.\n'
            f'Type `{context.prefix}algorithm` for more info.'
        )
        embed.set_thumbnail(url=context.bot.user.avatar_url)
        await context.send(embed=embed)

    @_interactive_setup.error
    async def _error_handler(self, context, error):
        if isinstance(error, MissingManageGuildPermissionAndGiveawayRole):
            await context.say_as_embed(str(error), color='error')


def setup(bot):
    bot.add_cog(GiveawayCommands(bot))

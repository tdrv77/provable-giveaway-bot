import discord

from django.db import models
from django.conf import settings
from django.utils import timezone

from db.apps.guilds.models import DiscordGuild
from db.apps.users.models import DiscordUser
from utils.objects import get_user_obj

from utils.time import process_elapsed_time_text


class Giveaway(models.Model):
    creator = models.ForeignKey(DiscordUser, related_name='giveaways', on_delete=models.CASCADE)
    prize = models.CharField(max_length=200)
    winner_count = models.SmallIntegerField()
    participants = models.ManyToManyField(DiscordUser, related_name='+', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ending_at = models.DateTimeField()
    ended_at = models.DateTimeField(blank=True, null=True)
    ended_time_str = models.CharField(max_length=200)
    success = models.BooleanField(
        null=True,
        help_text=
        '• Yes: Giveaway happened successfully.<br/>'
        '• No: Giveaway failed due to a Discord exception.<br/>'
        '• Unknown: Giveaway happening.'
    )

    # Discord stuff
    guild = models.ForeignKey(DiscordGuild, related_name='giveaways', on_delete=models.CASCADE)
    channel_id = models.BigIntegerField(blank=True, null=True)
    message_id = models.BigIntegerField(blank=True, null=True)
    bot = None

    def __str__(self):
        return f'{self.prize} [{self.status}]'

    def mark_success(self, success: bool):
        self.refresh_from_db()
        self.success = success
        self.ended_at = timezone.now()
        self.save()

    @property
    def passed_ending_time(self):
        return timezone.now() > self.ending_at

    @property
    def status(self):
        return 'Ended' if self.ended_at else 'On going'

    @property
    def discord_channel(self):
        if not isinstance(self.bot, discord.Client):
            raise AttributeError('`bot` must be `discord.Client`.')
        return self.bot.get_channel(self.channel_id)

    async def discord_message(self):
        if not self.discord_channel:
            return None

        try:
            message = await self.discord_channel.fetch_message(self.message_id)
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
    def winners_discord(self):
        return '\n'.join([
            f'• <@{winner.user.discord_id}> | '
            f'Index: {winner.index} | '
            f'Nonce: {winner.nonce}'
            for winner in self.winners.all()
        ])

    @property
    def info_text(self):
        txt = (
            f'== Creator Information ==\n'
            f'• Discord Tag  : {self.creator.__str__()}\n'
            f'• Discord ID   : {self.creator.discord_id}\n\n'
            f'== Giveaway Information ==\n'
            f'• Prize        : {self.prize}\n'
            f'• Winner Count : {self.winner_count}\n'
            f'• Participants : {self.participants.count()}\n'
            f'• Sure Win     : {self.winner_count >= self.participants.count()}\n'
            f'• Created at   : {self.created_at:%H:%M:%S %A %B %d, %Y (%Z)}\n'
            f'• Ending at    : {self.ending_at:%H:%M:%S %A %B %d, %Y (%Z)}\n'
            f'• Ended at     : {"On going" if not self.ended_at else self.ended_at.strftime("%H:%M:%S %A %B %d, %Y (%Z)")}\n'
            f'• Success      : {self.success}\n'
            f'• Server       : {self.guild.name} [{self.guild.guild_id}]\n\n'
            f'== Winners Information ==\n'
            f'{"User Tag":^20}|{"User ID":^20}|{"Index":^8}|{"Nonce":^8}|\n'
        )
        if self.winners.exists():
            txt += '\n'.join([
                f'{winner.user.__str__():<20}|'
                f'{winner.user.discord_id:^20}|'
                f'{winner.index:>7} |'
                f'{winner.nonce:>7} |'
                for winner in self.winners.all()
            ])
        else:
            txt += f'{"None":=^60}'

        return txt

    @property
    def embed(self):
        if self.success is not None:
            title = 'GIVEAWAY ENDED'
            color = discord.Color.darker_grey()
            footer_text = 'Ended'
            time_remaining = 'Ended'
        else:
            title = f'<:emoji:{settings.REACT_EMOJI_ID}> Result-Provable Giveaway <:emoji:{settings.REACT_EMOJI_ID}>'
            color = settings.EMBED_DEFAULT_COLOR
            footer_text = 'Ends'
            time_remaining = self.time_remaining

        embed = discord.Embed(
            title=title,
            description=
            f'• Prize: **{self.prize}**\n'
            f'• Winners: **{self.winner_count}**\n'
            f'• Time remaining: **{time_remaining}**\n\n',
            timestamp=self.ending_at,
            color=color,
        )

        if self.winners.exists():

            embed.add_field(
                name='Winners',
                value=self.winners_discord
            )

        elif self.success is None:
            embed.description += f'React with <:emoji:{settings.REACT_EMOJI_ID}> to enter!'

        embed.set_author(
            name=str(self.id),
            icon_url='https://cdn.discordapp.com/attachments/536172933173739520/592980762500923392/id.png'
        )

        embed.set_footer(text=footer_text)

        return embed

    async def end(self, for_task=False, for_reroll=False, context=None):
        ga_message = await self.discord_message()

        if not ga_message:
            self.mark_success(False)
            print(f'Giveaway with ID [{self.id}] failed because the Discord message was not found.')
            return

        # bypass the ended criteria if for_task is False
        if for_task:
            criteria = self.passed_ending_time
        elif for_reroll:
            if self.success is None:
                await context.say_as_embed(
                    f'Your Giveaway (ID: `{self.id}`) still on going. '
                    f'Use `{context.prefix}end {self.id}` if you want to end it.'
                )
                return
            self.winners.all().delete()
            criteria = True
        else:
            if self.success is not None:
                await context.say_as_embed(
                    f'Your Giveaway (ID: `{self.id}`) already ended. '
                    f'Use `{context.prefix}reroll {self.id}` if you want to reroll it.'
                )
                return
            criteria = True

        if criteria:

            reaction = None
            for _react in ga_message.reactions:
                if _react.emoji.id == settings.REACT_EMOJI_ID:
                    reaction = _react
                    break

            if not reaction:
                self.mark_success(False)
                message = f'Giveaway with ID `{self.id}` ended because it has no reactions.'
                await self.send_completion_message(ga_message.channel, message=message)
                return await ga_message.edit(embed=self.embed)

            qualified_entries = []
            async for user in reaction.users():
                if not user.bot:
                    qualified_entries.append(user)

            if not qualified_entries:
                self.mark_success(True)
                message = f'Giveaway with ID `{self.id}` ended with no winners.'
                await self.send_completion_message(ga_message.channel, message=message)
                return await ga_message.edit(embed=self.embed)

            winners = []
            # sure win
            if len(qualified_entries) <= self.winner_count:
                for entry in qualified_entries:
                    _entry = WinnerEntry(entry, 0, 0)
                    winners.append(_entry)
            # chance win
            else:

                # loop until enough distinct winners
                while len(winners) < self.winner_count:

                    index, nonce = self.creator.pfair_randomize(len(qualified_entries))
                    sorted_entries = sorted(qualified_entries, key=lambda x: x.id)

                    winner = sorted_entries[index]
                    _entry = WinnerEntry(winner, index, nonce)

                    if _entry in winners:
                        continue

                    winners.append(_entry)

            # update winner list
            winner_objs = [
                Winner(
                    giveaway=self,
                    user=get_user_obj(winner.discord)[0],
                    index=winner.index,
                    nonce=winner.nonce)
                for winner in winners
            ]
            Winner.objects.bulk_create(winner_objs)

            # update participant list
            self.participants.add(*[get_user_obj(entry)[0] for entry in qualified_entries])

            # update the giveaway object
            self.mark_success(True)
            await self.send_completion_message(ga_message.channel)
            return await ga_message.edit(embed=self.embed)

        # only edit ongoing giveaway messages
        self.refresh_from_db()
        if not self.ended_at:
            await ga_message.edit(embed=self.embed)

    async def send_completion_message(self, ga_channel, message=None):

        if self.winners.exists():
            mentions = ', '.join(f'<@{discord_id}>' for discord_id in self.winners.values_list('user__discord_id', flat=True))
            await ga_channel.send(
                f'Congratulations!! {mentions} won **{self.prize}**!'
            )
        else:
            message = f'Giveaway ID `{self.id}` ended but everyone is chillin\' so no winner is selected~!' if not message else message
            await ga_channel.send(message)

    @property
    def time_remaining(self):
        if not self.passed_ending_time:
            return process_elapsed_time_text(self.ending_at - timezone.now())
        else:
            return 'Ended'


class Winner(models.Model):
    user = models.ForeignKey(DiscordUser, related_name='winners', on_delete=models.CASCADE)
    giveaway = models.ForeignKey(Giveaway, related_name='winners', on_delete=models.CASCADE)
    index = models.PositiveIntegerField()
    nonce = models.PositiveIntegerField()


class WinnerEntry(object):
    def __init__(self, discord_user, index, nonce):
        self.discord = discord_user
        self.index = index
        self.nonce = nonce

    def __str__(self):
        return f'{self.discord} <{self.index} {self.nonce}>'

    def __repr__(self):
        return f'{self.discord} <{self.index} {self.nonce}>'

    def __eq__(self, other):
        return self.discord == other.discord

    def __ne__(self, other):
        return self.discord != other.discord

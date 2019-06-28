import discord
from discord.ext import commands

from bot.validators import validate_input
from utils.core import generate_server_seed
from utils.objects import get_user_obj
from .helptexts import (
    _pfair_algorithm_brief, _pfair_algorithm_help,
    _pfair_myseed_brief, _pfair_myseed_help,
    _pfair_newseed_brief, _pfair_newseed_help,
)
from django.conf import settings

algorithm_explanation_embed = discord.Embed(
    title='Randomization Algorithm Explained',
    description=
    'There is nothing to guarantee a complete randomization as we are dealing with digital stuff. '
    'So a **provable**, **unmodified** "randomized" result is just better than a spooky, unprovable one.\n\n'
    'When someone is salty about your Giveaway result, use this to explain how the result is picked.\n\n',
    color=settings.EMBED_DEFAULT_COLOR
)
algorithm_explanation_embed.add_field(
    name='Required information to check for correct results',
    value=
    '• You must renew your **User Seed** first. This will get you a **Server Seed (Unhashed)**.\n'
    '• Collect the **Nonce**s from Giveaways you want to check for.\n'
    f'Use `{settings.BOT_PREFIX}result [Giveaway ID]` to get those info.'
)
algorithm_explanation_embed.add_field(
    name='Step 1: Check for Server Seed integrity',
    value=
    '• I use SHA512 to hash the **Server Seed**, you can copy the **Unhashed** version, '
    'and paste it [here](https://abunchofutils.com/u/computing/sha512-hash-calculator/).\n'
    '• Click on **Calculate**.\n'
    '• Check if the result (appearing in the box below on the web page) is the same as the **Hashed** version the bot provided.\n'
    '• If they are 100% identical, the result of your Giveaway is NOT modified.\n\n'
)
algorithm_explanation_embed.add_field(
    name='Step 2: Get your result from Randomization Algorithm',
    value=
    '• The algorithm uses the first 5 letters of generated HMAC. [Click here to generate]'
    '(https://www.freeformatter.com/hmac-generator.html)\n'
    '++ The first box is the combination of `[User Seed (before renewing)]-[Nonce]` (no brackets, and please notice that *dash*, senpai)\n'
    '++ Secret Key is the `Server Seed Unhashed`\n'
    '++ Digest algorithm is `SHA512`\n'
    '• Convert those first 5 letters from the computed HMAC to decimal [here]'
    '(http://www.statman.info/conversions/hexadecimal.html)\n'
    '• Finally, divide the number with the **total number of participants in the checking Giveaway** '
    '(use Google by typing in `[That Decimal Number] mod [Total Participants]`)\n'
    '• Result of the calculation (**Remainder**) is the **Index** that represents in your Giveaway results.\n\n'
)
algorithm_explanation_embed.add_field(
    name='Step 3: Crosscheck the results',
    value=
    '• Note that in order to pick a winner, the bot first sorts (ascending) participants by their Discord ID. '
    'This adds an extra layer of randomness as participants randomly join.\n'
    '• Then with the **Remainder**, a winner is picked based on his/her **Index** in the list of sorted participants.\n'
    '• This will repeat until the bot picks enough **distinct winners** as you tell it when creating the Giveaway.\n'
)
algorithm_explanation_embed.add_field(
    name='Values Used Explanation',
    value=
    f'• **User Seed** - One of the factor to determine the randomness '
    f'while giving you the ability to check for results (only after renewing). '
    f'You can specify it by using `{settings.BOT_PREFIX}newseed [User Seed]`.\n'
    f'• **Nonce** - A number that increases by 1 when your Provable Fairness Information is used to generate a random Index once. '
    f'When picking winners, if the same winner is selected (same Index), **Nonce would increase**, until enough number of '
    f'distinct winners are met.'
    f'• **Server Seed - Hashed** - Hashed version of **Server Seed**, given to you in order to check for the result\'s integrity.\n'
    f'• **Server Seed - Unhashed** - The actual Server Seed, used as Secret Key to check for result and its integrity.'
)
algorithm_explanation_embed.add_field(
    name='Extras',
    value=
    '• Since you have the power to specify whatever **User Seed** is, I have no idea what the result would be. '
    'So long as your Server Seed has its integrity, your Giveaway results are provable, unmodified, and saving some salt.\n'
    '• All these steps are ignored when participants are fewer than the number of winners :shrug:'
)


class ProvableFairnessCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.__cog_name__ = 'Provable Fairness Commands'

    @commands.command(name='algorithm', help=_pfair_algorithm_help, brief=_pfair_algorithm_brief)
    async def _explain_pfair_algorithm(self, context):
        await context.send(embed=algorithm_explanation_embed)

    @commands.command(name='myseed', help=_pfair_myseed_help, brief=_pfair_myseed_brief)
    async def _check_self_pfair_information(self, context):
        user_obj, _ = get_user_obj(context.author)
        embed = discord.Embed(
            title=f'[{str(context.author)}]\'s Provable Fairness Information',
            color=settings.EMBED_DEFAULT_COLOR
        )
        embed.add_field(
            name='User Seed',
            value=f'```{user_obj.user_seed or "N/A"}```',
            inline=False
        )
        embed.add_field(
            name='Nonce',
            value=f'```{user_obj.nonce}```',
            inline=False
        )
        embed.add_field(
            name='Server Seed - Hashed',
            value=f'```{user_obj.server_seed_hashed or "N/A"}```',
            inline=False
        )
        embed.set_thumbnail(url=context.author.avatar_url)
        await context.send(embed=embed)

    @commands.command(name='newseed', help=_pfair_newseed_help, brief=_pfair_newseed_brief)
    async def _generate_new_seed(self, context, *, new_seed=None):
        if not new_seed:
            new_seed = str(context.author.id)
        elif len(new_seed) > 200:
            await context.say_as_embed(
                'Your Seed cannot be longer than 200 characters.',
                color='error'
            )
            return

        user_obj, _ = get_user_obj(context.author)

        embed = discord.Embed(
            title=f'{str(context.author)}, you are about to update your Provable Fairness Information',
            description=
            f'You can use `{context.prefix}{context.invoked_with} [Your Seed]` to '
            'specify your customized seed (recommended).',
            color=settings.EMBED_DEFAULT_COLOR
        )
        embed.add_field(
            name='Current Information',
            value=
            f'[CURRENT] User Seed\n```\n{user_obj.user_seed or "N/A"}```\n'
            f'[CURRENT] Nonce\n```\n{user_obj.nonce}```\n'
            f'[CURRENT] Server Seed - Hashed\n```\n{user_obj.server_seed_hashed or "N/A"}```\n',
        )

        embed.add_field(
            name='New Information',
            value=
            f'[NEW] User Seed\n```\n{new_seed}```\n'
            f'[NEW] Nonce\n```\n0```\n'
            f'[NEW] Server Seed - Hashed\n```\nRandomized```\n'
            f'[CURRENT] Server Seed - Unhashed\n```\nObtained after renewing```\n'
            '**Renew? (y/n)**'
        )
        await context.say_as_embed(embed=embed)

        response = await validate_input(context, inputs=['y', 'yes', 'n', 'no'])
        if response is False:
            return

        # stores current server seed to display before changing
        current_ss = user_obj.server_seed

        user_obj.user_seed = new_seed
        user_obj.server_seed = generate_server_seed()
        user_obj.nonce = 0
        user_obj.save()

        embed = discord.Embed(
            title=f'Provable Fairness Information for {str(context.author)} updated',
            description=
            f'[CURRENT] User Seed```{user_obj.user_seed}```\n'
            f'[CURRENT] Nonce```{user_obj.nonce}```\n'
            f'[CURRENT] Server Seed - Hashed```{user_obj.server_seed_hashed}```\n'
            f'[PREVIOUS] Server Seed - Unhashed```{current_ss or "N/A"}```',
            color=discord.Color.green()
        )

        await context.say_as_embed(embed=embed)

    @_explain_pfair_algorithm.error
    @_check_self_pfair_information.error
    @_generate_new_seed.error
    async def _error_handler(self, context, error):
        pass


def setup(bot):
    bot.add_cog(ProvableFairnessCommands(bot))

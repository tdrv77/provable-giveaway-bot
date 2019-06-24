import discord
import traceback
from discord.ext import commands
from django.conf import settings


class CustomContext(commands.Context):
    async def say_as_embed(
            self,
            description=None, title=None,
            embed=None, color='info',
            delete_after=None,
            footer_text=None,
            image_url=None,
            thumb_url=None,
    ):
        """Make the bot say as an Embed.
        Passing an 'embed' will send it instead.
        Shortcut for color kwarg: 'info' (default), 'warning', 'error', 'success'
        """

        if color == 'info':
            color = discord.Color.teal()
        elif color == 'warning':
            color = discord.Color.gold()
        elif color == 'error':
            color = discord.Color.red()
        elif color == 'success':
            color = discord.Color.green()

        if embed is None:

            embed = discord.Embed(
                title=title,
                description=description,
                colour=color)

            if image_url:
                embed.set_image(url=image_url)

            if thumb_url:
                embed.set_thumbnail(url=thumb_url)

            if footer_text:
                embed.set_footer(text=footer_text)

        message = await self.send(embed=embed, delete_after=delete_after)

        return message


class CustomBot(commands.Bot):

    async def on_ready(self):
        print('------')
        print(f'Logged in as: {self.user.name} (ID: {self.user.id})')
        print('------')
        presence = f'Prefix: {self.command_prefix}' if not settings.DEBUG else 'sensei anone'
        await self.change_presence(activity=discord.Game(name=presence))

    async def on_message(self, message):
        ctx = await self.get_context(message, cls=CustomContext)
        await self.invoke(ctx)

    async def on_command_error(self, context, error):

        if isinstance(error, commands.MissingRole):
            await context.say_as_embed(
                f'{context.author.mention}, you must have **<@&{error.missing_role}>** role to use this command!',
                color='error', delete_after=5)
            await context.message.delete()
            return

        if isinstance(error, commands.BadArgument):
            await context.say_as_embed(str(error), color='error')
            return

        if isinstance(error, commands.MissingRequiredArgument) and context.command.qualified_name != 'help':
            prefix = context.prefix
            command_name = context.invoked_with
            embed = discord.Embed(
                title=f'How to use the `{command_name}` command',
                description=
                context.command.help.format(prefix=prefix, command_name=command_name),
                color=settings.EMBED_DEFAULT_COLOR
            )
            await context.send(embed=embed)
            return

        await super().on_command_error(context, error)

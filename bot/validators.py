import asyncio

PREDEFINED_RESPONSES = [
    'n', 'no', 'cancel',
]


async def validate_input(context, inputs, **kwargs):
    """
    Validates the `inputs` as a list in the same channel.
    [Optional] `author`: Is the context.author if not specified, otherwise it's
    a discord.py User object, or a list of User objects.
    [Optional] `allow_cancel`: Allows the author to cancel the validation
    with words described in PREDEFINED_RESPONSES & the invoked command,
    to return False. Defaults to True.
    [Optional] `timeout`: Specifies the duration (seconds) for the validation to timeout.
    If None, it won't timeout until the bot dies. Default to 180.
    [Optional] `only_dm`: Sets whether the authors response is allowed only in DM or not.
    Default: False.

    Returns discord.py's Message object if passed.
    Returns False if failed.
    """

    authors = kwargs.get('authors', [context.author])
    allow_cancel = kwargs.get('allow_cancel', True)
    timeout = kwargs.get('timeout', 180)
    only_dm = kwargs.get('only_dm', False)

    if type(authors) != list:
        authors = [authors, ]

    if context.command.parent:
        prefixed_command = f'{context.prefix}{context.command.parent} {context.invoked_with}'
    else:
        prefixed_command = f'{context.prefix}{context.invoked_with}'

    def message_checker(message):
        if only_dm:
            if message.guild is not None:
                return False

            if message.content.lower() in PREDEFINED_RESPONSES + [prefixed_command, ] and allow_cancel:
                return True
            elif inputs is None:
                return True
            elif message.content.lower() in inputs:
                return True

            return False

        if message.channel == context.channel and message.author in authors:
            if message.content.lower() in PREDEFINED_RESPONSES + [prefixed_command, ] and allow_cancel:
                return True
            elif inputs is None:
                return True
            elif message.content.lower() in inputs:
                return True

            return False

        return False

    try:
        response = await context.bot.wait_for('message', check=message_checker, timeout=timeout)
    except asyncio.TimeoutError:
        await context.say_as_embed(
            f'You took too long to respond, please type `{prefixed_command}` to start over.', color='warning')
        return False

    if response.content.lower() in ['cancel', 'n', 'no']:
        await context.say_as_embed(
            f'Process canceled. Type `{prefixed_command}` if you want to start over.', color='warning')
        return False

    if response.content.lower().startswith(prefixed_command):
        await context.say_as_embed(
            'Process canceled because you initialized another one.', color='warning')
        return False

    return response

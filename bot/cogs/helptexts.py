# Help Commands
_help_brief = 'Shows this help message.'
_help_help = (
    'Format: ```{prefix}{command_name} [command name]```\n'
    f'Shows the help message.\n'
    f'If a `command name` is specified, shows help message for that command (Optional).'
)

# Giveaway Commands
_ga_create_brief = (
    'Interactively setup a Giveaway.'
)
_ga_create_help = (
    'Format: ```{prefix}{command_name}```\n'
    f'{_ga_create_brief}\n'
    f'You must have at least **Manage Server** permission or have **Giveaway** role to use this command.'
)

_ga_end_params = 'Format: ```{prefix}{command_name} [Giveaway ID]```\n'
_ga_end_brief = (
    'End your Giveaway.'
)
_ga_end_help = _ga_end_params + _ga_end_brief


_ga_reroll_brief = (
    'Reroll your Ended Giveaway.'
)
_ga_reroll_help = _ga_end_params + _ga_reroll_brief


_ga_delete_brief = (
    'Delete your Giveaway.'
)
_ga_delete_help = _ga_end_params + _ga_delete_brief


_ga_result_brief = (
    'Retrieve Result for your Giveaway.'
)
_ga_result_help = _ga_end_params + _ga_result_brief

# Provable Fairness Commands
_pfair_params = 'Format: ```{prefix}{command_name}```\n'
_pfair_algorithm_brief = (
    'Explains the Randomization Algorithm and how you can check for correctness of your Giveaway result.'
)
_pfair_algorithm_help = _pfair_params + _pfair_algorithm_brief

_pfair_myseed_brief = (
    'Shows your Provable Fairness Information.'
)
_pfair_myseed_help = _pfair_params + _pfair_algorithm_brief

_pfair_newseed_params = 'Format: ```{prefix}{command_name} [User Seed]```\n'

_pfair_newseed_brief = (
    'Generates new Provable Fairness Information.'
)
_pfair_newseed_help = _pfair_newseed_params + _pfair_algorithm_brief + (
    '\nPlease use `{prefix}algorithm` to learn more about the feature.'
)

# Provable-Result Givewaway Bot
## Introduction
**Discord's Giveaway Bot just got a lot better!**
This bot was made as an entry for **Discord Hackweek #1 (2019)**

This bot will help you:
- **Specify end date/time for your giveaway like you normally do**. No more weird suffixes and prefixes to show the bot where the hour/minute is.
- **Provide yourself with a Giveaway ID**, then you can `end`, `reroll`, `delete`, or retrieve your giveaway's `result` as a `*.txt` file. No more Discord Developer mode to get that spoopy Message ID.
- **Prove the randomness of the Giveaway result**, in case someone is salty and throws some hate at RNGesus.

## Requirements
This bot uses **Python (v.3.6+)** for logic and **PostgreSQL (v.10+)** to handle database and transactions. So make sure to have them prepared on your machine.

Main packages used:
- [discord.py](https://discordpy.readthedocs.io/en/latest/) - Main handler for the bot and its logic.
- [django](https://www.djangoproject.com/) - Django's ORM to handle transactions to the database.
- [dateparser](https://dateparser.readthedocs.io/en/latest/) - User input's date and time recognition that increases the bot's Intelligence by 100.
- [python-decouple](https://github.com/henriquebastos/python-decouple/) - Discord Staff tells you not to disclose your bot token, so here it is to fulfill this.

More detailed required packages can be found in the [`requirements.txt`](requirements.txt)

## Installation guide
- Clone this repo.
- Edit the [`.env-example`](.env-example) file with your `BOT_TOKEN`.
- In the same file, set `DATABASE_NAME`, `DATABASE_USER`, and `DATABASE_PASSWORD` as your PostgreSQL database's name, its owner user and password.
- Rename [`.env-example`](.env-example) to `.env`.
- `cd` to the repo's root directory (where the [`requirements.txt`](requirements.txt) is).
- Create a Python environment and activate it (`virtualenv` is a good choice).
- Run `pip install -r requirements.txt` and wait for it to install required packages.
- Run `python3 manage.py migrate` to apply database schemas.
- Finally, run `python3 run.py` to run the bot.
- [Optional] Run `python3 manage.py runserver` to run the bot's Admin Panel where its data is displayed cool and all. (You will need to create a superuser account using `python3 manage.py createsuperuser` to login into the Admin Panel.)

## Bot Permissions
- **Read Messages** and **Send Messages** (for interaction with bot)
- **Attach Files** (for `result` command)
- **Add Reactions** and **Use External Emojis** (for a cool and customized reaction emoji)
## Commands
### Default Prefix 
`.ga` - Changeable by modifying `BOT_PREFIX`
### Giveaway Commands
#### Restrictions
- User must have **Manage Server** permission OR **Giveaway** role to use the below commands.
- User must invoke the commands inside a server (not a DM).
#### Commands
- `create` : Interactively setup a Giveaway.
- `end [Giveaway ID]` : End your On going Giveaway.
- `reroll [Giveaway ID]` : Reroll your Ended Giveaway.
- `delete [Giveaway ID]` : Delete your Giveaway.
- `result [Giveaway ID]` : Retrieve Result of your Ended Giveaway (result will be sent as a `*.txt` file).

### Provable Fairness Commands
#### Restrictions
- No restrictions
#### Commands
- `algorithm` : Explains the Randomization Algorithm and how you can check for correctness of your Giveaway result.
- `myseed` : Shows your Provable Fairness Information.
- `newseed [User Seed]` : Generates new Provable Fairness Information to get the old ones and prove your results.

### Help Commands
#### Restrictions
- No restrictions
#### Commands
- `help` : Shows help message, type `help [command name]` to get detailed help for that command.

## Future plans
Considering how big the current `GiveawayBot#2381` is, this bot is supposed to be hosted by someone generous enough to afford a good machine that can handle a good few thousands of giveaways.

I will eventually extend this bot and host it myself for better experience creating giveaways on Discord.

## Contribution
### Author
- An Tran - PonPon#4444
### Contributors
*This place is currently empty :HaHaa:*

## License
This project is licensed under [GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/).
    
Provable-Result Giveaway Discord Bot | Copyright (C) 2019, An Tran

    This program is free software: you can redistribute it and/or modify 
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

For more information, see [LICENSE.md](LICENSE.md)
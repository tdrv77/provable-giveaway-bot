# Provable-Result Givewaway Bot
## Introduction
**Discord's Giveaway Bot just got a lot better!**
This bot was made as an entry for **Discord Hackweek #1**

This bot will help you:
- **Specify end date/time for your giveaway like you normally do**. No more weird suffixes and prefixes to show the bot where the hour/minute is.
- **Provide yourself with a Giveaway ID**, then you can `end`, `reroll`, `delete`, or retrieve your giveaway's `result` as a `*.txt` file. No more Discord Developer mode to get that spoopy Message ID.
- **Prove the randomness of the Giveaway result**, in case someone is salty and throws some hate at RNGesu.

## Requirements
This bot uses **Python (v.3.6+)** for logic and **PostgreSQL (v.10+)** to handle database and transactions. So make sure to have them prepared on your machine.

Main packages used:
- [discord.py](https://discordpy.readthedocs.io/en/latest/) - Main handler for the bot and its logic.
- [django](https://www.djangoproject.com/) - Django's ORM to handle transactions to the database.
- [dateparser](https://dateparser.readthedocs.io/en/latest/) - User input's date and time that increase the bot's Intelligence by 100.
- [python-decouple](https://github.com/henriquebastos/python-decouple/) - Discord Staff tells you not to disclose your bot token, so here it is to fulfill this.

More detailed required packages can be found in the [requirements.txt](requirements.txt)

## Installation
Considering how big the current `GiveawayBot#2381` is, this bot is supposed to be hosted by someone generous enough to afford a good machine that can handle a good few thousands of giveaways.

Below is the installtion guide:
- Clone this repo.
- Edit the [`.env-example`](.env-example) file with your `BOT_TOKEN`.
- In the same file, set `DATABASE_NAME`, `DATABASE_USER`, and `DATABASE_PASSWORD` as your PostgreSQL database's name, its owner user and password.
- Rename [`.env-example`](.env-example) to `.env`.
- `cd` to the repo's root directory (where the [`requirements.txt`](requirements.txt) is).
- Create a Python environment and activate it (`virtualenv` is a good choice).
- Run `pip install -r requirements.txt` and wait for it to install required packages.
- Run `python3 manage.py migrate` to apply database schemas.
- Finally, run `python3 run.py` to run the bot.
- *Optional* Run `python3 manage.py runserver` to run the bot's Admin Panel where its data is display cool and all. (You will need to create a superuser account using `python3 manage.py createsuperuser` to login into the Admin Panel.)

## Commands
### Giveaway Commands
- `create` : Interactively setup a Giveaway.
- `end` : End your On going Giveaway.
- `reroll` : Reroll your Ended Giveaway.
- `delete` : Delete your Giveaway.
- `result` : Retrieve Result of your Ended Giveaway (result will be sent as a `*.txt` file).

### Provable Fairness Commands
- `algorithm` : Explains the Randomization Algorithm and how you can check for correctness of your Giveaway result.
- `myseed` : Shows your Provable Fairness Information.
- `newseed` : Generates new Provable Fairness Information.

### Help Commands
- `help` : Shows help message, type `help [command name]` to get detailed help for that command.

## License
This repository is licensed under [GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/).

For more information, see [LICENSE.md](LICENSE.md)
## Contribution
*Under construction*

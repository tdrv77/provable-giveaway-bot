from math import floor


def check_time_elapsed(td):
    """
    Returns a tuple of day, hour, minute, second.
    'td' is a timedelta object or integer number in seconds.
    """
    if td.__class__.__name__ == 'timedelta':
        total_seconds = td.total_seconds()
    else:
        total_seconds = td

    day = floor(total_seconds / 24 / 60 / 60)
    hour = floor(total_seconds / 60 / 60 - day * 24)
    minute = floor(total_seconds / 60 - day * 24 * 60 - hour * 60)
    second = floor(total_seconds - day * 24 * 60 * 60 - hour * 60 * 60 - minute * 60)

    return day, hour, minute, second


def process_elapsed_time_text(td):
    """
    Returns a string that shows the time elapsed in this format:
    x day(s) x hour(s) x minute(s) x second(s)
    if any of the x == 0, the indicator and x will not show.
    if any of the x == 1, the indicator will be in singular form
    """

    day, hour, minute, second = check_time_elapsed(td)

    if day > 0:
        elapsed_time_text = f'{day} days {hour} hours {minute} minutes {second} seconds'
    elif hour > 0:
        elapsed_time_text = f'{hour} hours {minute} minutes {second} seconds'
    elif minute > 0:
        elapsed_time_text = f'{minute} minutes {second} seconds'
    else:
        elapsed_time_text = f'{second} seconds'

    if day == 1:
        elapsed_time_text = elapsed_time_text.replace('days', 'day')
    if hour == 1:
        elapsed_time_text = elapsed_time_text.replace('hours', 'hour')
    if minute == 1:
        elapsed_time_text = elapsed_time_text.replace('minutes', 'minute')
    if second == 1:
        elapsed_time_text = elapsed_time_text.replace('seconds', 'second')
    if second == 0:
        elapsed_time_text = elapsed_time_text.replace('0 seconds', '').strip()

    return elapsed_time_text

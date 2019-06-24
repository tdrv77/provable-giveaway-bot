import random
import string


def generate_server_seed():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=300))

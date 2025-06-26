import random

def generate_unique_slug(length=6):
    """Generates a random, unique slug of a given length (default 6).
    Uses base58 characters (excludes 0, O, I, l to avoid visual ambiguity).
    Base58 characters: 123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz
    """
    chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    return ''.join(random.choice(chars) for _ in range(length))
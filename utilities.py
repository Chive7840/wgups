import re
import os
from typing import Any, Match
from pathlib import Path

SOURCE_FILE = Path(__file__).resolve()
SOURCE_DIR = SOURCE_FILE.parent
ROOT_DIR = SOURCE_DIR.parent
EMBEDDED_DIR = SOURCE_DIR / '__WGUPS Package File.csv'


def debug(*args) -> None:
    if 'DEBUG' in os.environ:
        print(*args)


def deadline_to_minutes(deadline: str) -> int:
    """
    Converts the provided deadline time string into an integer used
    for calculating travel time for use when recording status change timestamps
    :param deadline:
    :return Time string converted into a usable integer:
    """
    hrs, mins = list(map(int, deadline.split(":")))
    if 0 <= hrs < 24 and 0 <= mins < 60:
        return hrs * 60 + mins


def convert_minutes(minutes: float) -> str:
    """
    Returns a human friendly readable time string instead of a sum of time as minutes
    :param minutes:
    :return Time string:
    """
    return f'{int(minutes / 60)}:{int(minutes % 60):02}'


def new_line_removal(a_match: Match[str]) -> str:
    """
    Removes all the newline breaks present in the data for normalization purposes
    :param a_match:
    :return Concatenated string with newlines removed:
    """
    tmp_match = a_match.group(0)[0]
    if tmp_match == '\n':
        return ' ' if tmp_match == '\n' else tmp_match.upper()


def normalize_address(address: str) -> str:
    """
    Between the two files, the initialism for the cardinal directions is used
    interchangably with the full words. This method normalizes the addresses to contain
    just the initials
    :param address:
    :return Normalized address:
    """
    corrected = re.sub(r'(?i)(north|east|south|west|\n)', new_line_removal,
                       address.strip())
    return corrected


def MaxPrimeFactor(integer) -> int:
    """
    Used to generate prime numbers for use in HashTable resizing
    :param integer:
    :return Next prime number:
    """
    prime_factor = 1
    n = 2

    while n <= integer / n:
        if integer % n == 0:
            prime_factor = n
            integer /= n
        else:
            n += 1

        if prime_factor < integer:
            prime_factor = integer

        return prime_factor


def prime_num_gen():
    """
    Used by the HashTable to resize when necessary
    :return No return value:
    """
    prime_nums = [2]
    while True:
        prime_num = prime_nums[-1]
        yield prime_num

        while any(map(lambda x: prime_num % x == 0, prime_nums)):
            prime_num += 1

        prime_nums.append(prime_num)

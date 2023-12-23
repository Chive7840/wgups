import re
import os
from typing import Any, Match


def debug(*args) -> None:
    if 'DEBUG' in os.environ:
        print(*args)


def deadline_to_minutes(deadline: str) -> int:
    hrs, mins = list(map(int, deadline.split(":")))
    if 0 <= hrs < 24 and 0 <= mins < 60:
        return hrs * 60 + mins


def MaxPrimeFactor(integer):
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
    prime_nums = [2]
    while True:
        prime_num = prime_nums[-1]
        yield prime_num

        while any(map(lambda x: prime_num % x == 0, prime_nums)):
            prime_num += 1

        prime_nums.append(prime_num)


def convert_minutes(minutes: float) -> str:
    return f'{int(minutes / 60)}:{int(minutes % 60):02}'


def cardinal_to_letter(nl_match: Match[str]) -> str:
    tmp_match = nl_match.group(0)[0]
    if tmp_match == '\n':
        return ' ' if tmp_match == '\n' else tmp_match.upper()


def clean_address(address: str) -> str:
    corrected = re.sub(r'(?i)(north|east|south|west|\n)', cardinal_to_letter,
                       address.strip())
    return corrected


class ColorCoding:
    UWHITE = '\033[4;37m'
    UCYAN = '\033[4;36m'
    UGREEN = '\033[4;32m'
    URED = '\033[4;31m'
    UBLUE = '\033[4;34m'

    @staticmethod
    def uwhite(highlight: Any) -> str:
        return f'{ColorCoding.UWHITE}{highlight}{ColorCoding.UWHITE}'

    @staticmethod
    def ucyan(highlight: Any) -> str:
        return f'{ColorCoding.UCYAN}{highlight}{ColorCoding.UWHITE}'

    @staticmethod
    def ugreen(highlight: Any) -> str:
        return f'{ColorCoding.UGREEN}{highlight}{ColorCoding.UWHITE}'

    @staticmethod
    def ured(highlight: Any) -> str:
        return f'{ColorCoding.URED}{highlight}{ColorCoding.UWHITE}'

    @staticmethod
    def ublue(highlight: Any) -> str:
        return f'{ColorCoding.UBLUE}{highlight}{ColorCoding.UWHITE}'


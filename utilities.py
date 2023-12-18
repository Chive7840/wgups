import re
import os
from typing import Any, Match



def __direction_to_letter(m: Match[str]) -> str:
    match = m.group(0)[0]
    return ' ' if match == '\n' else match.upper()


def normalize_address(address: str) -> str:
    return re.sub(r'(?i)(north|south|east|west|\n)', __direction_to_letter, address.strip())


class ColorCoding:
    UWHITE = "\033[4;37m"
    UCYAN = "\033[4;36m"
    UGREEN = "\033[4;32m"
    URED = "\033[4;31m"
    UBLUE = "\033[4;34m"

    @staticmethod
    def white(highlight: Any) -> str:
        return f'{ColorCoding.UWHITE}{highlight}{ColorCoding.UWHITE}'

    @staticmethod
    def cyan(highlight: Any) -> str:
        return f'{ColorCoding.UCYAN}{highlight}{ColorCoding.UWHITE}'

    @staticmethod
    def green(highlight: Any) -> str:
        return f'{ColorCoding.UGREEN}{highlight}{ColorCoding.UWHITE}'

    @staticmethod
    def red(highlight: Any) -> str:
        return f'{ColorCoding.URED}{highlight}{ColorCoding.UWHITE}'

    @staticmethod
    def blue(highlight: Any) -> str:
        return f'{ColorCoding.UBLUE}{highlight}{ColorCoding.UWHITE}'


def debugger(*args) -> None:
    if 'DEBUGGER' in os.environ:
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
    return f'{int(minutes / 60)}:{int(minutes % 60)}:00'

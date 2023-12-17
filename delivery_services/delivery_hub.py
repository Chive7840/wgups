from enum import Enum, auto
import re
from typing import Optional, TYPE_CHECKING


class DeliveryHub:
    def __init__(self, dh_name: str, dh_address: str) -> None:
        self.dh_name = dh_name
        self.dh_address = dh_address

    def __str__(self) -> str:
        return self.dh_address

    def __addr__(self) -> str:
        return self.dh_address

    def __hash_address__(self) -> int:
        return hash(self.dh_address)


if TYPE_CHECKING:
    pass

EOD = 24 * 60


class Package:
    class Status(Enum):
        AT_HUB = auto()
        EN_ROUTE = auto()
        DELIVERED = auto()

    @staticmethod
    def parse_time(time: str) -> int:
        if time == 'EOD':
            return EOD

        hours, minutes, meridiem = re.search(
            r'(?i)(\d?\d):(\d\d) ([ap]m)', time).groups()
        offset = 0 if meridiem.lower() == 'am' else 12
        return ((int(hours) + offset) * 60) + int(minutes)

    __required_truck: Optional[int] = None
    __loaded_at: Optional[float] = None
    __delivered_by: Optional[int] = None
    delivered_at: Optional[float] = None
    wrong_address = False
    __available_at = 0.0
    dependencies: set[Package]
    dependent_packages: set[int]
    __delivery_number = 0

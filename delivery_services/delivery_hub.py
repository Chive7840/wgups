from __future__ import annotations
from typing import Union
import utilities


class DeliveryHub:
    def __init__(self, dh_name: str, dh_address: str) -> None:
        self.dh_name = dh_name
        self.dh_address = utilities.clean_address(dh_address)

    def __str__(self) -> str:
        return self.dh_address

    def __repr__(self) -> str:
        return self.dh_address

    def __eq__(self, other: Union[str, DeliveryHub]) -> bool:
        return hash(self) == hash(other)

    def __hash__(self) -> int:
        return hash(self.dh_address)
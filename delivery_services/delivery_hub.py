from __future__ import annotations
from typing import Union
import utilities


class DeliveryHub:
    def __init__(self, dh_name: str, dh_address: str):
        self.dh_name = dh_name
        # Normalizes addresses as they are used for hash keys
        self.dh_address = utilities.normalize_address(dh_address)

    def __str__(self) -> str:
        """
        Dunder method for returning a human-friendly representation of the delivery hub object
        :return Delivery hub address:
        """
        return self.dh_address

    def __repr__(self) -> str:
        """
        Printable string representation of the delivery hub object
        :return Address string:
        """
        return self.dh_address

    def __eq__(self, other: Union[str, DeliveryHub]) -> bool:
        """
        An equality which compares the hash code of the input to the hash code
        of the delivery hub object and returns a value based on if they match
        :param other:
        :return True or False:
        """
        return hash(self) == hash(other)

    def __hash__(self) -> int:
        """
        Must agree with the __eg__ method this ensures that the inputs have equal hashes
        :return hash code for the hub address:
        """
        return hash(self.dh_address)
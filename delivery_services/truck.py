from __future__ import annotations
from utilities import debugger
from typing import Union, TYPE_CHECKING
from delivery_services.pkg_handler import PkgObject
from data_services.graph import DHGraph

if TYPE_CHECKING:
    from delivery_hub import DeliveryHub
    from pkg_handler import PkgObject
    from data_services.graph import DHGraph

class Truck:
    truck_number = 0

    @staticmethod
    def get_truck_number() -> int:
        Truck.truck_number += 1
        return Truck.truck_number

    @staticmethod
    def elapsed_time(time: float):
        return (8 * 60) + (time / 18 * 60)

    total_miles: float = 0
    pkg_lst = [PkgObject]
    __truck_number: int
    deliveries_completed = 0

    def __init__(self) -> None:
        self.__truck_number = self.get_truck_number()
        self.pkg_lst = []

    def deliver_packages(self, dh_graph: DHGraph[Union[DeliveryHub, str]]) -> None:
        self.deliveries_completed += 1
        prev: str = ''
        curr: str = "BASE"
        for pkg in self.pkg_lst:
            curr = pkg.addr
            self.total_miles += dh_graph.get_distance(prev, curr)
            pkg.delivered_status(self)
            truck_info = (f'Truck number {self.truck_number} \ndelivered package, ID# {pkg.pkg_id}\n'
                          f'at {pkg.delivered_time}. The package was delivered to {pkg.addr}'
                          f'after traveling {self.total_miles} miles.')
            debugger(truck_info)

        self.pkg_lst.clear()
        self.total_miles += dh_graph.get_distance(curr, "BASE")
        debugger(f'Truck number {self.truck_number} returned to base with {round(self.total_miles, 1)}'
                 f'total miles traveled.')

    def truck_cap(self) -> int:
        return 16 - len(self.pkg_lst)

    def load_truck(self, pkg: PkgObject) -> None:
        if self.truck_full():
            raise Exception

        pkg.en_route_status(self)
        self.pkg_lst.append(pkg)

    def get_time_elapsed(self) -> float:
        return self.elapsed_time(self.total_miles)

    def truck_full(self):
        return len(self.pkg_lst) == 16

    def truck_empty(self) -> bool:
        return len(self.pkg_lst) == 0

    def truck_location(self) -> str:
        if self.truck_empty():
            return 'At Base'
        else:
            return self.pkg_lst[-1].addr


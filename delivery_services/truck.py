from __future__ import annotations
import logging
from utilities import debug, convert_minutes, SOURCE_DIR
from typing import Union, TYPE_CHECKING

# Creates a logger using the module name
logger = logging.getLogger(__name__)
# Specifies that only DEBUG level logs should be saved
logger.setLevel(logging.DEBUG)
# Specifies the name and path for the log file
truck_log_file = SOURCE_DIR / 'delivery_services' / 'delivery_logs' / 'truck.log'
routing_handler = logging.FileHandler(truck_log_file)
# Specifies a format for the logs being recorded
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
# Sets the handler's formatter
routing_handler.setFormatter(formatter)
# Adds the file handler to the logger
logger.addHandler(routing_handler)


if TYPE_CHECKING:
    from delivery_hub import DeliveryHub
    from pkg_handler import PkgObject
    from data_services.graph import DHGraph


class Truck:
    truck_number = 0

    @staticmethod
    def __get_truck_number() -> int:
        """
        Returns the assigned truck number for a truck object
        Also iterates on the truck number allowing for any number of trucks to be created
        :return Truck Number as an integer:
        """
        Truck.truck_number += 1
        return Truck.truck_number

    @staticmethod
    def elapsed_time(time: float):
        """
        Calculates the elapsed travel time, assuming no accidents and a constant 18
        miles per hour maximum speed using the number of miles traveled as an input
        :param time:
        :return:
        """
        return (8 * 60) + (time / 18 * 60)

    total_miles: float = 0
    pkg_lst: list[PkgObject]
    truck: int
    deliveries_completed = 0

    def __init__(self):
        self.truck = self.__get_truck_number()
        self.pkg_lst = []

    def load_truck(self, pkg: PkgObject):
        """
        Adds packages to a trucks storage list. This simulates loading the truck
        If for some reason thye truck is already full an exception is raised and logged
        :param pkg:
        :return No return value:
        """
        if self.truck_full():
            logger.exception(f'Package ID: {pkg.pkg_id} cannot be loaded onto {self.__get_truck_number()}.')
            raise Exception

        pkg.enroute_status(self)
        self.pkg_lst.append(pkg)

    def max_truck_capacity(self) -> int:
        return 16 - len(self.pkg_lst)

    def get_time_elapsed(self) -> float:
        return self.elapsed_time(self.total_miles)

    def truck_full(self):
        return len(self.pkg_lst) == 16

    def truck_empty(self) -> bool:
        return len(self.pkg_lst) == 0

    def truck_location(self) -> str:
        return 'HUB' if self.truck_empty() else self.pkg_lst[-1].address

    def deliver_packages(self, dh_graph: DHGraph[Union[DeliveryHub, str]]):
        """
        Simulates a truck delivering packages and stores the information for use later
        :param dh_graph:
        :return:
        """
        self.deliveries_completed += 1
        prev: str = ''
        curr: str = 'HUB'
        for pkg in self.pkg_lst:
            prev = curr
            curr = pkg.address
            self.total_miles += dh_graph.get_distance(prev, curr)
            pkg.set_delivered_status(self)
            truck_info = [f'truck #: {self.truck}']
            truck_info += f'delivered: {pkg.pkg_id}'
            truck_info += f'at {convert_minutes(pkg.delivered_at_time)} o\'clock local time.'
            truck_info += f'The package was delivered at {pkg.address}'
            truck_info += f'after having traveled a total of {round(self.total_miles, 1)} miles.'
            logger.debug(truck_info)

        self.pkg_lst.clear()
        self.total_miles += dh_graph.get_distance(curr, 'HUB')
        debug(f'Truck number {self.truck_number} returned to base with {round(self.total_miles, 1)}'
                 f'total miles traveled.')


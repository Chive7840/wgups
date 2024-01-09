from __future__ import annotations
from utilities import convert_minutes, normalize_address, SOURCE_DIR
import logging
import re
from enum import auto, Enum
from typing import Optional, cast, TYPE_CHECKING

# Creates a logger using the module name
logger = logging.getLogger(__name__)
# Specifies that only DEBUG level logs should be saved
logger.setLevel(logging.DEBUG)
# Specifies the name and path for the log file
pkg_log_file = SOURCE_DIR / 'delivery_services' / 'delivery_logs' / 'pkg_handler.log'
routing_handler = logging.FileHandler(pkg_log_file)
# Specifies a format for the logs being recorded
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
# Sets the handler's formatter
routing_handler.setFormatter(formatter)
# Adds the file handler to the logger
logger.addHandler(routing_handler)

if TYPE_CHECKING:
    from delivery_services.truck import Truck

EOD = 60 * 24


class PkgObject:
    # Used to implement the status codes for each segment of the delivery process
    class StatusCode(Enum):
        AT_HUB = auto()
        ENROUTE = auto()
        DELIVERED = auto()

    @staticmethod
    def time_formatter(time: str) -> int:
        """
        This converts a provided time string into an integer for use in tracking deliveries
        and sorting packages.
        :param time:
        :return Integer of converted time string:
        """
        if time == 'EOD':
            return EOD

        hrs, mins, am_pm = re.search(r'(?i)(\d?\d):(\d\d) ([ap]m)', time).groups()
        if am_pm.lower() == 'am':
            offset = 0
        else:
            offset = 12
        return ((int(hrs) + offset) * 60) + int(mins)

    __truck_tracker: Optional[int] = None
    __truck_loaded_at_time: Optional[float] = None
    __delivered_by_truck: Optional[int] = None
    delivered_at_time: Optional[float] = None
    wrong_address = False
    __available_when = 0.0
    pkg_dependencies: set[PkgObject]
    depend_pkgs: set[int]
    __route_number = 0

    def __init__(self, pkg_id: str, addr: str, city: str, state: str, postal_code: str,
                 deadline: str, weight: str, note: str):
        self.depend_pkgs = set[int]()
        self.pkg_dependencies = set[PkgObject]()
        self.pkg_id = int(pkg_id)
        self.str_addr = addr
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.delivery_promise = self.time_formatter(deadline)
        self.weight = int(weight)
        self.__status = self.StatusCode.AT_HUB
        self.__note_processor(note)
        self.address = normalize_address(f'{self.str_addr} ({self.postal_code})')

    def __str__(self) -> str:
        """
        Takes some of the package attributes and structures them for print out if called
        :param self:
        :return Comma delimited string
        """
        delivery_promise = convert_minutes(self.delivery_promise)
        pkg_info = [f'pkg_id: {self.pkg_id},', f'pkg_addr: {self.address},', f'pkg_status: {self.__status},',
                    f'delivery_promise: {self.delivery_promise},']

        if self.delivered_at_time is not None:
            pkg_info.append(f'Delivery Time: {convert_minutes(self.delivered_at_time)},')
            on_time = self.delivered_at_time < self.delivery_promise
            pkg_info.append(f'Delivered On Time: {on_time}')

        return str.join(',', pkg_info)

    def pkg_prioritizer(self, time_stamp: float) -> bool:
        """
        Returns a package's location as at the hub
        when it's delivery promise time is less than the EOD calculation if that is less than the
        specified time
        :param self:
        :param time_stamp:
        :return at_hub status and when the package will be available:
        """
        return self.check_at_hub_status() and self.delivery_promise < EOD and self.__available_when <= time_stamp

    def pkg_delivery_eligibility(self, truck: Truck, exclude_pkg: set[PkgObject] = set()) -> bool:
        """
        Checks to see if a package is ot at the hub, flagged for having the wrong address, is available for delivery
        while the truck is en route, and if a package needs to be delivered with other packages.
        :param self:
        :param truck:
        :param exclude_pkg:
        :return boolean response for a package's delivery eligibility:
        """

        if self.wrong_address:
            return False

        if self.__available_when > truck.get_time_elapsed():
            return False

        if not self.check_at_hub_status():
            return False

        if self.__truck_tracker is not None and self.__truck_tracker != truck.truck:
            return False

        available_pkgs = True
        exclude_pkg.add(self)

        # Recursive for loop which compares all packages in a provided list of packages
        for pkgs in [p for p in self.pkg_dependencies if p not in exclude_pkg]:
            available_pkgs = pkgs.pkg_delivery_eligibility(truck, exclude_pkg)
        return available_pkgs

    def __note_processor(self, note: str) -> None:
        """
        Parses through the provided notes text field looking for:
        - Package Availability times
        - Specific truck numbers
        - Specific groupings of packages that must be delivered together
        - The last criteria is for the package with the incorrect address.
        :param self:
        :param note:
        :return Replaces the text in the package object as it's being constructed:
        """

        if len(note) == 0:
            pass

        elif note_match := re.search(r'\d?\d:\d\d [ap]m', note):
            self.__available_when = self.time_formatter(note_match.group(0))

        elif note_match := re.search(r'truck (\d)', note):
            self.__truck_tracker = int(note_match.group(1))

        elif 'delivered with' in note:
            self.depend_pkgs = set[int](map(int, re.findall(r'\d+', note)))
            logger.info(f'{self.depend_pkgs}')

        else:
            self.address = ''
            self.__available_when = self.time_formatter('10:20 am')
            self.wrong_address = True

    def enroute_status(self, truck: Truck) -> None:
        """
        Sets a truck's current status to enroute assuming it's not already marked as enroute or
        if it's been on a different truck once already
        :param self:
        :param truck:
        :return No return value:
        """
        if self.__status == self.StatusCode.ENROUTE:
            logger.exception(f'Status: {self.__status}\t Truck: {truck}')
            raise Exception

        if (self.__truck_tracker or truck.truck) != truck.truck:
            logger.exception(f'Required Truck: {self.__truck_tracker}\t Truck: {truck.truck}')
            raise Exception

        self.__delivered_by_truck = truck.truck
        self.__truck_loaded_at_time = truck.get_time_elapsed()
        self.__status = self.StatusCode.ENROUTE

    def set_delivered_status(self, truck: Truck) -> None:
        """
        If a package is already delivered and on the truck an exception is logged and the program is stopped
        Updates the number of packages delivered by the truck
        :param self:
        :param truck:
        :return:
        """
        if self.__status == self.StatusCode.DELIVERED:
            logger.exception(f'Status: {self.__status}\t Truck: {truck}')
            raise Exception

        self.__status = self.StatusCode.DELIVERED
        self.delivered_at_time = truck.get_time_elapsed()
        self.__route_number = truck.deliveries_completed

    def pkg_is_delivered(self) -> bool:
        """
        Changes a package's status code to Delivered when called
        :param self:
        :return Updates a package's status to Delivered in the object:
        """
        return self.__status == self.StatusCode.DELIVERED

    def check_at_hub_status(self) -> bool:
        """
        A method for checking if the current status of a package object is "AT_HUB"
        :param self:
        :return A bool value (True/False) that determines if the current status is "AT_HUB":
        """
        return self.__status == self.StatusCode.AT_HUB

    def address_correction_available(self, time: float) -> bool:
        """
        This method is specifically for package number 9 although it could be used for any
        package with a wrong address.
        :param self:
        :param time:
        :return returns False until a time stamp after the listed time it will be available is passed:
        """
        # The address for package # 9 is not available until 10:20 AM
        # this provides a means to track that time and ensure the package
        # is delivered after the address is corrected

        return self.wrong_address and self.__available_when <= time

    def corrected_address(self):
        """
        Changing package number 9's wrong_address flag to False makes it eligible for delivery.
        In addition to changing the bool flag, the correct address is applied to the package object
        :param self:
        :return No return value:
        """
        self.wrong_address = False
        self.address = '410 S State St (84111)'
        self.str_addr = '410 S State St'
        self.postal_code = '84111'

    def get_pkg_status(self, time: int) -> str:
        """
        Prints out the status of a package based on a provided time stamp using human
        recognizable output
        :param self:
        :param time:
        :return  Concatenated string which is derived based on the inputted time:
        """

        if self.__available_when > time:
            return f'Package will be available at {convert_minutes(self.__available_when)}.'
        load_time = cast(float, self.__truck_loaded_at_time)
        if time < load_time:
            return (f'The package is currently at the base, it is expected to be loaded at'
                    f' {convert_minutes(load_time)}.')

        delivery_time = cast(float, self.delivered_at_time)
        truck_num = cast(int, self.__delivered_by_truck)
        if time < delivery_time:
            return (f'The package is on truck number {truck_num}. It was loaded at {convert_minutes(load_time)} and'
                    f' the expected time of delivery is {convert_minutes(delivery_time)}.')

        return f'The package was delivered at {convert_minutes(delivery_time)} by truck {truck_num}.'

    def promise_format(self) -> str:
        """
        Converts the deadline paramater into something recognizable by a human
        :param self:
        :return Delivery deadline as a time :
        """
        if self.delivery_promise == EOD:
            return 'EOD'

        return convert_minutes(self.delivery_promise)

    def get_pkg_information(self, time: int) -> str:
        """
        Provides a printout of all the packages variables as a concatenated string for us in testing
        and returning information to user based queries.
        :param self:
        :param time:
        :return Concatenated string:
        """

        pkg_info = [f'Package ID {self.pkg_id};\t']
        if (self.delivered_at_time or float('inf')) <= time:
            pkg_info.append(f'is currently marked as {self.StatusCode.DELIVERED};\t')
        elif (self.__truck_loaded_at_time or float('inf')) <= time:
            pkg_info.append(f'is currently {self.StatusCode.ENROUTE};\t')
        else:
            pkg_info.append(f'is currently {self.StatusCode.AT_HUB};\t')

        if self.promise_format() == 'EOD':
            pkg_info.append(f'the package will be delivered by 10:00 pm;\t')
        else:
            pkg_info.append(f'the scheduled delivery time is {self.promise_format()} am;\t')

        if (self.__truck_loaded_at_time or float('inf')) <= time:
            pkg_info.append(f'the package was loaded onto truck {self.__delivered_by_truck};\t')

        if (self.delivered_at_time or float('inf')) <= time:
            delivered_ontime = self.delivered_at_time < self.delivery_promise
            if delivered_ontime:
                pkg_info.append(f'it was delivered on time at {convert_minutes(self.delivered_at_time)} am;\t')
            else:
                pkg_info.append(f'it was not delivered on time at {convert_minutes(self.delivered_at_time)} am;\t')

            pkg_info.append(f'by truck {self.__delivered_by_truck};\t')
            pkg_info.append(f'on route {self.__route_number}')

        return str.join('\t', pkg_info)

    def all_pkg_info_status(self, time: int) -> str:
        """
        Returns information for all package attributes as well as the delivery time and status
        :param time:
        :return String of package status/status information:
        """
        pkg_info = [f'Package ID: {self.pkg_id};\t',f'Address: {self.address};\t', f'City: {self.city};\t',
                    f'State: {self.state};\t', f'Postal Code {self.postal_code};\t, Weight(kg): {self.weight};\t']

        if self.promise_format() == 'EOD':
            pkg_info.append(f'Delivery Promise: EOD;\t')
        else:
            pkg_info.append(f'Delivery Promise: {self.promise_format()} am;\t')

        if (self.delivered_at_time or float('inf')) <= time:
            pkg_info.append(f'{self.StatusCode.DELIVERED};\t')
        elif (self.__truck_loaded_at_time or float('inf')) <= time:
            pkg_info.append(f'{self.StatusCode.ENROUTE};\t')
        else:
            pkg_info.append(f'{self.StatusCode.AT_HUB};\t')

        if (self.delivered_at_time or float('inf')) <= time:
            delivered_ontime = self.delivered_at_time < self.delivery_promise
            if delivered_ontime:
                pkg_info.append(f'Delivery Time: {convert_minutes(self.delivered_at_time)} am')
            else:
                pkg_info.append(f'it was not delivered on time at {convert_minutes(self.delivered_at_time)} am')

        return str.join('\t', pkg_info)

    def __hash__(self) -> int:
        return hash(self.pkg_id)

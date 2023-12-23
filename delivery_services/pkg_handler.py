from __future__ import annotations
from utilities import ColorCoding, convert_minutes, clean_address
from pathlib import Path
import logging
import re
from enum import auto, Enum
from typing import Optional, cast, TYPE_CHECKING


# Creates a logger using the module name
logger = logging.getLogger(__name__)
# Specifies that only DEBUG level logs should be saved
logger.setLevel(logging.DEBUG)
# Specifies the name and path for the log file
pkg_log_path = Path.cwd() / 'delivery_services' / 'delivery_logs' / 'pkg_handler.log'
routing_handler = logging.FileHandler(pkg_log_path)
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
    class StatusCodes(Enum):
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
    __num_pkgs_delivered = 0

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
        self.__status = self.StatusCodes.AT_HUB
        self.__note_processor(note)
        self.address = clean_address(f'{self.str_addr} ({self.postal_code})')

    def __str__(self) -> str:
        """
        Takes some of the package attributes and structures them for print out if called
        :param self:
        :return Color coded and concatenated string of a package's status:
        """
        delivery_promise = convert_minutes(self.delivery_promise)
        pkg_info = [f'pkg_id: {self.pkg_id}', f'pkg_addr: {self.address}', f'pkg_status: {self.__status}',
                    f'delivery_promise: {self.delivery_promise}']

        if self.delivered_at_time is not None:
            pkg_info.append(f'Delivery Time: {convert_minutes(self.delivered_at_time)}')
            on_time = self.delivered_at_time < self.delivery_promise
            if on_time:
                highlight = ColorCoding.ugreen(on_time)
            else:
                highlight = ColorCoding.ured(on_time)
            pkg_info.append(f'Delivered On Time: {highlight}')

        return str.join(', ', pkg_info)

    def pkg_prioritizer(self, time_stamp: float) -> bool:
        """
        Returns a package's location as at the hub
        when it's delivery promise time is less than the EOD calculation if that is less than the
        specified time
        :param self:
        :param time_stamp:
        :return at_hub status and when the package will be available:
        """
        return self.set_at_hub() and self.delivery_promise < EOD and self.__available_when <= time_stamp

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

        if not self.set_at_hub():
            return False

        if self.__truck_tracker is not None and self.__truck_tracker != truck.truck_number:
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
        if self.__status == self.StatusCodes.ENROUTE:
            logger.exception(f'Status: {self.__status}\t Truck: {truck}')
            raise Exception

        if (self.__truck_tracker or truck.truck_number) != truck.truck_number:
            logger.exception(f'Required Truck: {self.__truck_tracker}\t Truck: {truck.truck_number}')
            raise Exception

        self.__delivered_by_truck = truck.truck_number
        self.__truck_loaded_at_time = truck.get_time_elapsed()
        self.__status = self.StatusCodes.ENROUTE

    def set_delivered_status(self, truck: Truck) -> None:
        """
        If a package is already delivered and on the truck an exception is logged and the program is stopped
        Updates the number of packages delivered by the truck
        :param self:
        :param truck:
        :return:
        """
        if self.__status == self.StatusCodes.DELIVERED:
            logger.exception(f'Status: {self.__status}\t Truck: {truck}')
            raise Exception

        self.__status = self.StatusCodes.DELIVERED
        self.delivered_at_time = truck.get_time_elapsed()
        self.__num_pkgs_delivered = truck.deliveries_completed

    def pkg_is_delivered(self) -> bool:
        """
        Changes a package's status code to Delivered when called
        :param self:
        :return Updates a package's status to Delivered in the object:
        """
        return self.__status == self.StatusCodes.DELIVERED

    def set_at_hub(self) -> bool:
        """
        Initializes the 'Status' variable field for packages as they are loaded into the hash table.
        :param self:
        :return Updates the package object directly:
        """
        return self.__status == self.StatusCodes.AT_HUB

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

    def __get_pkg_status(self, time: int) -> str:
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
            return (f'The package is on {truck_num}. It was loaded at {convert_minutes(load_time)} and'
                    f'the expected time of delivery is {delivery_time}')

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

    def __get_pkg_information(self, time: int) -> str:
        """
        Provides a printout of all the packages variables as a concatenated string for us in testing
        and returning information to user based queries.
        :param self:
        :param time:
        :return Concatenated string:
        """
        pkg_info = [f'Pkg ID {self.pkg_id}', f'Address: {self.address}']
        if (self.delivered_at_time or float('inf')) <= time:
            pkg_info.append(ColorCoding.ugreen(self.StatusCodes.DELIVERED))
        elif (self.__truck_loaded_at_time or float('inf')) <= time:
            pkg_info.append(ColorCoding.ucyan(self.StatusCodes.ENROUTE))
        else:
            pkg_info.append(ColorCoding.ublue(self.StatusCodes.AT_HUB))

        pkg_info.append(f'Package Delivery Promise: {self.promise_format()}')

        if (self.__truck_loaded_at_time or float('inf')) <= time:
            pkg_info.append(f'Package loaded at {convert_minutes(self.__truck_loaded_at_time)}')
            pkg_info.append(f'onto truck number {self.__truck_tracker} during delivery #: {self.__num_pkgs_delivered}')

        if (self.delivered_at_time or float('inf')) <= time:
            pkg_info.append(f'The package was delivered at {convert_minutes(self.delivered_at_time)}')
            pkg_ontime = self.delivered_at_time < self.delivery_promise
            if pkg_ontime:
                txt_color = ColorCoding.ugreen(pkg_ontime)
            else:
                txt_color = ColorCoding.ured(pkg_ontime)
            pkg_info.append(f'Package delivered on time{txt_color}')

        return str.join(';', pkg_info)

    def __hash__(self) -> int:
        return hash(self.pkg_id)


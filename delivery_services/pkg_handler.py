from __future__ import annotations
from utilities import ColorCoding, convert_minutes, clean_address
import logging
import re
from enum import auto, Enum
from typing import Optional, cast, TYPE_CHECKING

# Creates a logger using the module name
logger = logging.getLogger(__name__)
# Specifies that only DEBUG level logs should be saved
logger.setLevel(logging.DEBUG)
# Specifies the name and path for the log file
routing_handler = logging.FileHandler('../delivery_services/delivery_logs/pkg_handler.log')
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
    # This class is used to track the stages of the last mile delivery progress
    class StatusCodes(Enum):
        AT_HUB = auto()
        ENROUTE = auto()
        DELIVERED = auto()

    @staticmethod
    def time_formatter(time: str) -> int:
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
    delivered_by_truck: Optional[int] = None
    delivered_at_time: Optional[float] = None
    __available_when = 0.0
    pkg_dependencies: set[PkgObject]
    depend_pkgs: set[int]
    num_pkgs_delivered = 0
    wrong_address = False

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
        self.status = self.StatusCodes.AT_HUB
        self.note_processor(note)
        self.address = clean_address(f'{self.str_addr} ({self.postal_code})')


    def __str__(self) -> str:
        delivery_promise = convert_minutes(self.delivery_promise)
        pkg_info = [f'pkg_id: {self.pkg_id}', f'pkg_addr: {self.address}', f'city: {self.city}',
                    f'state: {self.state}', f'postal_code: {self.postal_code}',
                    f'pkg_status: {self.status}', f'delivery_promise: {self.delivery_promise}']

        if self.delivered_at_time is not None:
            pkg_info.append(f'Delivery Time: {convert_minutes(self.delivered_at_time)}')
            on_time = self.delivered_at_time < self.delivery_promise
            if on_time:
                highlight = ColorCoding.ugreen(on_time)
            else:
                highlight = ColorCoding.ured(on_time)
            pkg_info.append(f'Delivered On Time: {highlight}')

        return str.join(', ', pkg_info)

    def promise_format(self) -> str:
        if self.delivery_promise == EOD:
            return 'EOD'

        return convert_minutes(self.delivery_promise)

    def en_route_status(self, truck) -> None:
        if self.status == self.StatusCodes.ENROUTE:
            logger.exception(f'Status: {self.status}\t Truck: {truck}')
            raise Exception

        if (self.__truck_tracker or truck.truck_number) != truck.truck_number:
            logger.exception(f'Required Truck: {self.__truck_tracker}\t Truck: {truck.truck_number}')
            raise Exception

        self.delivered_by_truck = truck.truck_number
        self.__truck_loaded_at_time = truck.get_time_elapsed()
        self.status = self.StatusCodes.ENROUTE

    def delivered_status(self, truck) -> None:
        if self.status == self.StatusCodes.DELIVERED:
            logger.exception(f'Status: {self.status}\t Truck: {truck}')
            raise Exception

        self.status = self.StatusCodes.DELIVERED
        self.delivered_at_time = truck.get_time_elapsed()
        self.num_pkgs_delivered = truck.deliveries_completed

    def at_base(self) -> bool:
        return self.status == self.StatusCodes.AT_HUB

    def pkg_delivered(self) -> bool:
        return self.status == self.StatusCodes.DELIVERED

    def pkg_prioritizer(self, time_stamp: float) -> bool:
        return self.at_base() and self.delivery_promise < EOD and self.__available_when <= time_stamp

    def address_correction_available(self, time: float):

        # The address for package # 9 is not available until 10:20 AM
        # this provides a means to track that time and ensure the package
        # is delivered after the address is corrected

        return self.wrong_address and self.__available_when <= time

    def corrected_address(self):

        # This is the correct address for package # 9

        self.wrong_address = False
        self.address = '410 S State St (84111)'
        self.str_addr = '410 S State St'
        self.postal_code = '84111'

    def get_pkg_status(self, time: int) -> str:

        # Returns the status of a package at a requested time

        if self.__available_when > time:
            return f'Package will be available at {convert_minutes(self.__available_when)}.'
        load_time = cast(float, self.__truck_loaded_at_time)
        if time < load_time:
            return (f'The package is currently at the base, it is expected to be loaded at'
                    f' {convert_minutes(load_time)}.')

        delivery_time = cast(float, self.delivered_at_time)
        truck_num = cast(int, self.delivered_by_truck)
        if time < delivery_time:
            return (f'The package is on {truck_num}. It was loaded at {convert_minutes(load_time)} and'
                    f'the expected time of delivery is {delivery_time}')

        return f'The package was delivered at {convert_minutes(delivery_time)} by truck {truck_num}.'

    def pkg_delivery_eligibility(self, truck: Truck, exclude_pkg: set[PkgObject] = set()) -> bool:

        # Determines the eligibility of packages to be delivered by trucks

        if self.wrong_address:
            return False

        if self.__available_when > truck.get_time_elapsed():
            return False

        if not self.at_base():
            return False

        if self.__truck_tracker is not None and self.__truck_tracker != truck.truck_number:
            return False

        available_pkgs = True
        exclude_pkg.add(self)

        # Recursive for loop which compares all packages in a provided set

        for pkgs in [p for p in self.pkg_dependencies if p not in exclude_pkg]:
            available_pkgs = pkgs.pkg_delivery_eligibility(truck, exclude_pkg)
        return available_pkgs

    def note_processor(self, note: str) -> None:

        # In addition to blank notes there are a few packages that contain specific instructions
        # this function parses/prints the notes to obtain the instructions

        if len(note) == 0:
            pass

        elif note_match := re.search(r'\d?\d:\d\d [ap]m', note):
            self.__available_when = self.time_formatter(note_match.group(0))

        elif note_match := re.search(r'truck (\d)', note):
            self.__truck_tracker = int(note_match.group(1))

        elif 'delivered with' in note:
            self.depend_pkgs = set[int](map(int, re.findall(r'\d+', note)))

        else:
            self.address = ''
            self.__available_when = self.time_formatter('10:20 am')
            self.wrong_address = True

    def get_pkg_information(self, time: int) -> str:

        # When prompted this prints information about the package for a specified time

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
            pkg_info.append(f'onto truck number {self.delivered_by_truck} during delivery #: {self.num_pkgs_delivered}')

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

from __future__ import annotations
import re
from enum import auto, Enum
from typing import Optional, cast, TYPE_CHECKING
from utilities import ColorCoding, convert_minutes


if TYPE_CHECKING:
    from delivery_services.truck import Truck

EOD = 60 * 24


class PkgObject:
    # This class is used to track the stages of the last mile delivery progress
    class StatusCodes(Enum):
        AT_BASE = auto()
        ENROUTE = auto()
        DELIVERED = auto()

    @staticmethod
    def time_formatter(time: str) -> int:
        if time == 'EOD':
            return EOD

        hrs, mins = re.search(r'(?i)(\d?\d):(\d\d)', time).groups()
        return (int(hrs) * 60) + int(mins)

    availability = 0.0
    next_pkg: set[PkgObject]()
    depend_pkg: set[int]()
    pkgs_delivered = 0
    truck: Optional[int] = None
    truck_load_time: Optional[float] = None
    delivered_by_truck: Optional[int] = None
    delivered_time: Optional[float] = None
    wrong_address = False

    def __init__(self, pkg_id: str, addr: str, city: str, state: str, postal_code: str,
                 deliver_promise: str, weight: str, note: str):
        self.depend_pkg = set[int]()
        self.next_pkg = set[PkgObject]()
        self.pkg_id = int(pkg_id)
        self.addr = addr
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.delivery_promise = self.time_formatter(deliver_promise)
        self.weight = int(weight)
        self.status = self.StatusCodes.AT_BASE
        self.note_processor(note)

    def __str__(self) -> str:
        delivery_promise = convert_minutes(self.delivery_promise)
        pkg_info = [f'Package ID: {self.pkg_id}', f'Address: {self.addr}', f'City: {self.city}',
                    f'State: {self.state}', f'Postal Code: {self.postal_code}'
                                            f'Status: {self.status}', f'Delivery Promise: {delivery_promise}']

        if self.delivered_time is not None:
            pkg_info.append(f'Delivery Time: {convert_minutes(self.delivered_time)}')
            on_time = self.delivered_time < self.delivered_time
            if on_time:
                highlight = ColorCoding.UGREEN(on_time)
            else:
                ColorCoding.URED(on_time)
            pkg_info.append(f'Delivered On Time: {highlight}')

            return str.join(', ', pkg_info)

    def __hash__(self) -> int:
        return hash(self.pkg_id)

    def promise_format(self) -> str:
        if self.delivery_promise == EOD:
            return 'EOD'

        return convert_minutes(self.delivery_promise)

    def en_route_status(self, truck) -> None:
        if self.status == self.StatusCodes.ENROUTE:
            raise Exception

        if self.truck or truck.number != truck.number:
            raise Exception

        self.delivered_by_truck = truck.number
        self.truck_load_time = truck.get_truck_time_stamp()
        self.status = self.StatusCodes.ENROUTE

    def delivered_status(self, truck) -> None:
        if self.status == self.StatusCodes.DELIVERED:
            raise Exception

        self.pkgs_delivered = truck.deliveries_completed
        self.delivered_time = truck.get_truck_time_stamp()
        self.status = self.StatusCodes.DELIVERED

    def at_base(self) -> bool:
        return self.status == self.StatusCodes.AT_BASE

    def pkg_delivered(self) -> bool:
        return self.status == self.StatusCodes.DELIVERED

    def pkg_prioritizer(self, time_stamp: float) -> bool:
        return self.at_base() and self.delivery_promise < EOD and self.availability < time_stamp

    def note_processor(self, note: str) -> None:

        # In addition to blank notes there are a few packages that contain specific instructions
        # this function parses/prints the notes to obtain the instructions

        if len(note) == 0:
            pass

        elif match := re.search(r'\d?\d:\d\d', note):
            self.availability = self.time_formatter(match.group(0))

        elif match := re.search(r'truck (\d)', note):
            self.truck = int(match.group(1))

        elif 'delivered with' in note:
            self.depend_pkg = set[int](map(int, re.findall(r'd\+', note)))

        else:
            self.addr = ''
            self.availability = self.time_formatter('10:20')
            self.wrong_address = True

    def address_correction_available(self, time: float):

        # The address for package # 9 is not available until 10:20 AM
        # this provides a means to track that time and ensure the package
        # is delivered after the address is corrected

        return self.wrong_address and self.availability <= time

    def corrected_address(self):

        # This is the correct address for package # 9

        self.wrong_address = False
        self.addr = '410 S State St'
        self.postal_code = '84111'

    def get_pkg_information(self, time: int) -> str:

        # When prompted this prints information about the package for a specified time

        pkg_info = [f'Pkg ID {self.pkg_id}', f'Address: {self.addr}']
        if self.delivered_time or float('inf') <= time:
            pkg_info.append(ColorCoding.UGREEN(self.StatusCodes.DELIVERED))
        elif self.truck_load_time or float('inf') <= time:
            pkg_info.append(ColorCoding.UCYAN(self.StatusCodes.ENROUTE))
        else:
            pkg_info.append(ColorCoding.UBLUE(self.StatusCodes.AT_BASE))

        pkg_info.append(f'Package Delivery Promise: {self.delivery_promise}')

        if self.truck_load_time or float('inf') < time:
            pkg_info.append(f'Package loaded at {self.truck_load_time}, '
                            f'onto truck number {self.delivered_by_truck}')

        if self.delivered_time or float('inf') <= time:
            pkg_info.append(f'The package was delivered at {convert_minutes(self.delivered_time)}')
            pkg_ontime = self.delivered_time < self.delivery_promise
            if pkg_ontime:
                pkg_txt_color = ColorCoding.UGREEN(pkg_ontime)
            else:
                pkg_txt_color = ColorCoding.URED(pkg_ontime)
                pkg_info.append(f'Package delivered on time{pkg_txt_color}')

        return str.join('\t', pkg_info)

    def get_pkg_status(self, time: int) -> str:

        # Returns the status of a package at a requested time

        if self.availability > time:
            return f'Package will be available at {convert_minutes(self.availability)}.'

        load_time = cast(float, self.truck_load_time)
        if time < load_time:
            return (f'The package is currently at the base, it is expected to be loaded at'
                    f' {convert_minutes(load_time)}.')

        delivery_time = cast(float, self.delivered_time)
        truck_num = cast(int, self.delivery_promise)
        if time < delivery_time:
            return (f'The package is on {truck_num}. It was loaded at {convert_minutes(load_time)} and'
                    f'the expected time of delivery is {delivery_time}')

        return f'The package was delivered at {convert_minutes(delivery_time)} by truck {truck_num}.'

    def pkg_delivery_eligibility(self, truck: Truck, exclude_pkg: set[PkgObject] = set()) -> bool:

        # Determines the eligibility of packages to be delivered by trucks

        if self.availability > truck.get_time_elapsed():
            return False

        if self.wrong_address:
            return False

        if not self.at_base():
            return False

        if self.truck is not None and self.truck != truck.truck_number:
            return False

        available_pkgs = True
        exclude_pkg.add(self)

        # Recursive for loop which compares all packages in a provided set

        for pkgs in [p for p in self.next_pkg if p not in exclude_pkg]:
            available_pkgs = pkgs.pkg_delivery_eligibility(truck, exclude_pkg)
        return available_pkgs

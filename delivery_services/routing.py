# External libraries
import csv
from typing import Iterable, Union, cast
import logging

# Internal Modules
from delivery_services.truck import Truck
from delivery_services.delivery_hub import DeliveryHub
from delivery_services.pkg_handler import PkgObject
from data_services import DHGraph, HashTable

# Creates a logger using the module name
logger = logging.getLogger(__name__)
# Specifies that only DEBUG level logs should be saved
logger.setLevel(logging.DEBUG)
# Specifies the name and path for the log file
routing_handler = logging.FileHandler('../delivery_services/delivery_logs/routing.log')
# Specifies a format for the logs being recorded
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
# Sets the handler's formatter
routing_handler.setFormatter(formatter)
# Adds the file handler to the logger
logger.addHandler(routing_handler)


pkgs_file = '../input_files/__WGUPS Package File.csv'
distance_file = '../input_files/__WGUPS Distance Table.csv'

HUB = 'HUB'
time_at_base = 60 * 8

TRUCKS_ALL: list[Truck]
PKGS_ALL: HashTable[int, PkgObject]
GRAPH: DHGraph[Union[DeliveryHub, str]]


def find_nearest_hub(pkgs: Iterable[PkgObject], location: Union[str, DeliveryHub]) -> PkgObject:
    """
     T(n) = O(n)
     S(n) = O(1)
     :param: pkgs, location
     :return: PkgObject
    """
    min_dist = float("inf")
    closest_hub = None
    for pkg in pkgs:
        distance = GRAPH.get_distance(pkg.address, location)

        if distance < min_dist:
            min_dist = distance
            closest_hub = pkg
        if distance >= min_dist:
            logger.debug(f'Hub_A: {pkg.address} Hub_B: {location} Distance: {distance} Min: {min_dist}')
    return cast(PkgObject, closest_hub)


wrong_address = None


def route_trucks() -> int:
    """
    T(n) = O(n)
    S(n) = O(1)
    :param: None
    :return: delivered int
    """
    global wrong_address
    if wrong_address is None:
        wrong_address = [pkg[1] for pkg in PKGS_ALL if pkg[1].wrong_address]
    delivered = 0
    for truck in TRUCKS_ALL:
        delivered += len(truck.pkg_lst)
        truck.deliver_packages(GRAPH)
        if len(wrong_address) != 0:
            for pkg in wrong_address:
                if pkg.address_correction_available(truck.get_truck_number()):
                    pkg.corrected_address()
                    wrong_address.remove(pkg)
    return delivered


def sort_packages(pkgs: Iterable[PkgObject]):
    '''
    Sorts packages onto trucks and attempts to create the shortest possible route
    T(n) = O(n)
    S(n) = O(1)
    :param pkgs:
    :return: None
    '''
    pkg_count = float('inf')
    while pkg_count > 2:
        pkg_count = 0
        for truck in TRUCKS_ALL:
            if truck.truck_full():
                continue
            __min = float('inf')
            nearest = None
            for pkg in pkgs:
                if pkg.pkg_delivery_eligibility(truck):
                    pkg_count += 1
                    distance = GRAPH.get_distance(truck.truck_location(), pkg.address)
                    if distance < __min:
                        __min = distance
                        nearest = pkg

            if nearest is not None:
                truck.load_truck(nearest)


def pkg_importer() -> tuple[HashTable[int, PkgObject], HashTable[str, list[PkgObject]]]:
    """
    T(n) = O(n)
    S(n) = O(n)
    :param: None
    :return: pkgs, pkg_dest
    """
    pkgs = HashTable[int, PkgObject]()
    pkg_dest_table = HashTable[str, list[PkgObject]]()
    dependency_table = HashTable[int, set[PkgObject]]()

    with (open('../input_files/__WGUPS Package File.csv') as pkg_f):
        pkg_reader = csv.reader(pkg_f, delimiter=';')
        next(pkg_reader)
        for row in pkg_reader:
            n_pkg = PkgObject(*row)
            pkgs.insert(n_pkg.pkg_id, n_pkg)
            if (lst_of_pkgs := pkg_dest_table.get(n_pkg.address)) is None:
                lst_of_pkgs: list[PkgObject] = []
                pkg_dest_table.insert(n_pkg.address, lst_of_pkgs)
            lst_of_pkgs.append(n_pkg)
            for depend_pkg in n_pkg.depend_pkgs:
                if (depend_pkg_set := dependency_table.get(depend_pkg)) is None:
                    depend_pkg_set = set()
                    dependency_table.insert(depend_pkg, depend_pkg_set)
                depend_pkg_set.add(n_pkg)
            for k_pkg in dependency_table.get(n_pkg.pkg_id) or []:
                k_pkg.pkg_dependencies.add(n_pkg)
                n_pkg.pkg_dependencies.add(k_pkg)
    return pkgs, pkg_dest_table


def priority_first(pkg_dest_table: HashTable[str, list[PkgObject]]):
    """
    T(n): O(n)
    S(n): O(n)
    :param pkg_dest_table:
    :return: None
    """
    priority_pkgs = set([pkg[1] for pkg in PKGS_ALL if any([pkg[1].pkg_prioritizer(x.get_time_elapsed())
                                                            and pkg[1].pkg_delivery_eligibility(x) for x in
                                                            TRUCKS_ALL])])
    TRUCKS_ALL.sort(key=lambda x: x.total_miles)
    for truck in TRUCKS_ALL:
        while not truck.truck_full() and len(priority_pkgs) != 0:
            nearest = find_nearest_hub(priority_pkgs, truck.truck_location())
            depend_pkg = nearest.pkg_dependencies
            # print(depend_pkg)  # TODO: REMOVE
            for pkg in depend_pkg:
                depend_pkg = depend_pkg.union(cast(set[PkgObject], pkg.pkg_dependencies))
            depend_pkg.add(nearest)
            if truck.truck_cap() > len(depend_pkg):
                while len(depend_pkg) != 0:
                    pkg = find_nearest_hub(depend_pkg, truck.truck_location())
                    depend_pkg.discard(pkg)
                    if not pkg.at_base():
                        continue
                    priority_pkgs.discard(pkg)
                    truck.load_truck(pkg)
                    for pkg in pkg_dest_table.get(pkg.address) or []:
                        if not truck.truck_full() and pkg.pkg_delivery_eligibility(truck):
                            priority_pkgs.discard(pkg)
                            truck.load_truck(pkg)


def deliver_remainder_of_pkgs() -> int:
    """
    T(n) = O(n)
    S(n) = O(n)
    :param: None
    :return: int
    """
    # TODO: REMOVE
    pkg_lst = []
    for pkg in PKGS_ALL:
        if pkg[1].at_base():
            pkg_lst.append(pkg[1])

    # non_priority_pkgs = [pkg[1] for pkg in PKGS_ALL if pkg[1].at_base()]

    sort_packages(pkg_lst)
    return route_trucks()


def distance_finder() -> DHGraph[Union[DeliveryHub, str]]:
    """
    T(n) = O(n**2)
    S(n) = O(n**2)
    :param: None
    :return: Graphed Delivery Hubs
    """
    dh_graph = DHGraph[Union[DeliveryHub, str]]()
    with open(distance_file) as dist_f:
        delivery_hubs: list[DeliveryHub] = []
        hub_reader = csv.reader(dist_f, delimiter=';', quotechar='"')
        for dh_name, dh_addr, *dh_dists in hub_reader:
            hub = DeliveryHub(dh_name, dh_addr)
            dh_graph.insert_hub(hub)
            delivery_hubs.append(hub)
            for (h, dist) in enumerate(dh_dists):
                dh_graph.insert_edge(hub, delivery_hubs[h], float(dist))
        return dh_graph


def auto_router() -> tuple[HashTable[int, PkgObject], list[Truck]]:
    """
    Assume:
    m = number of delivery hubs
    n = number of packages
        T(n) = O(m**2) + O(n)
        S(n) = O(m**2) + O(n)
    :param: None
    :return: PKGS_ALL, TRUCKS
    """
    global PKGS_ALL
    global TRUCKS_ALL
    global GRAPH
    # O(n)
    TRUCKS_ALL = [Truck(), Truck()]
    PKGS_ALL, pkg_dest_table = pkg_importer()
    # O(m**2)
    GRAPH = distance_finder()
    priority_pending_delivery = True
    while priority_pending_delivery:
        priority_first(pkg_dest_table)
        # TODO: priority_first is running an infinite loop
        # breakpoint()
        if priority_pending_delivery := any([not truck.truck_empty() for truck in TRUCKS_ALL]):
            deliver_remainder_of_pkgs()
    remaining_pkgs = sum(map(lambda x: 0 if x[1].pkg_delivered() else 1, PKGS_ALL))
    while remaining_pkgs != 0:
        remaining_pkgs -= deliver_remainder_of_pkgs()
    return PKGS_ALL, TRUCKS_ALL



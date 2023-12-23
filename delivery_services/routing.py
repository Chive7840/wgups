# External libraries
from pathlib import Path
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
routing_log_folder = Path.cwd() / 'delivery_services' / 'delivery_logs' / 'routing.log'
routing_handler = logging.FileHandler(routing_log_folder)
# Specifies a format for the logs being recorded
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
# Sets the handler's formatter
routing_handler.setFormatter(formatter)
# Adds the file handler to the logger
logger.addHandler(routing_handler)

pkgs_file = Path.cwd() / 'input_files' / '__WGUPS Package File.csv'
distance_file = Path.cwd() / 'input_files' / '__WGUPS Distance Table.csv'

HUB = 'HUB'
time_at_base = 60 * 8

__TRUCKS_ALL: list[Truck]
__PKGS_ALL: HashTable[int, PkgObject]
__GRAPH: DHGraph[Union[DeliveryHub, str]]
wrong_address_pkg = None


def __find_nearest_hub(pkgs: Iterable[PkgObject], location: Union[str, DeliveryHub]) -> PkgObject:
    """
     T(n) = O(n)
     S(n) = O(1)
     Compares the distances between a package destination and specified delivery point
     and forces the returned tuple to retain their types
     :param: pkgs, location
     :return PkgObject;
    """
    min_dist = float("inf")
    closest_hub = None
    for pkg in pkgs:
        distance = __GRAPH.get_distance(pkg.address, location)

        if distance < min_dist:
            min_dist = distance
            closest_hub = pkg
    return cast(PkgObject, closest_hub)


def route_trucks() -> int:
    """
    T(n) = O(n)
    S(n) = O(1)
    Iterates over the list of trucks and calls the method for deliverying packages.
    Additionally, it checks to see if enough time has passed for
    the wrong address packages to have their address corrected. If enough time has passed it updates
    the address and removes it from the list of packages with an incorrect address.
    :param: None
    :return: Number of packages delivered
    """
    global wrong_address_pkg
    if wrong_address_pkg is None:
        wrong_address_pkg = [pkg[1] for pkg in __PKGS_ALL if pkg[1].wrong_address]
    delivered = 0
    for truck in __TRUCKS_ALL:
        delivered += len(truck.pkg_lst)
        truck.deliver_packages(__GRAPH)
        if len(wrong_address_pkg) != 0:
            for pkg in wrong_address_pkg:
                if pkg.address_correction_available(truck.get_time_elapsed()):
                    pkg.corrected_address()
                    wrong_address_pkg.remove(pkg)
    return delivered


def sort_packages(pkgs: Iterable[PkgObject]):
    """
    T(n) = O(n)
    S(n) = O(1)
    Sorts packages between the trucks in an attempt to create the shortest path possible
    with the provided trucks and packages.
    :param pkgs:
    :return No return value:
    """
    pkg_count = float('inf')
    while pkg_count > 2:
        pkg_count = 0
        for truck in __TRUCKS_ALL:
            if truck.truck_full():
                continue
            __min = float('inf')
            nearest = None
            for pkg in pkgs:
                if pkg.pkg_delivery_eligibility(truck):
                    pkg_count += 1
                    distance = __GRAPH.get_distance(truck.truck_location(), pkg.address)
                    if distance < __min:
                        __min = distance
                        nearest = pkg

            if nearest is not None:
                truck.load_truck(nearest)


def pkg_importer() -> tuple[HashTable[int, PkgObject], HashTable[str, list[PkgObject]]]:
    """
    T(n) = O(n)
    S(n) = O(n)
    This parses the reformatted packages csv file and converts the package information into a list
    of PkgObjects and then inserts them into a table containing all packages for a given destination
    :param: None
    :return tuple(PkgObject Table, PkgObject Destination Table):
    """
    pkgs = HashTable[int, PkgObject]()
    pkg_dest_table = HashTable[str, list[PkgObject]]()
    dependency_table = HashTable[int, set[PkgObject]]()

    with (open(pkgs_file) as pkg_f):
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


def __priority_first(pkg_dest_table: HashTable[str, list[PkgObject]]):
    """
    T(n): O(n)
    S(n): O(n)
    Builds a list of priority packages based on a call to the eligiblity method
    Loads the packages onto a truck if they are a priority package
    :param pkg_dest_table:
    :return None:
    """
    priority_pkgs = set([pkg[1] for pkg in __PKGS_ALL if any([pkg[1].pkg_prioritizer(x.get_time_elapsed())
                                                              and pkg[1].pkg_delivery_eligibility(x) for x in
                                                              __TRUCKS_ALL])])
    __TRUCKS_ALL.sort(key=lambda x: x.total_miles)
    for truck in __TRUCKS_ALL:
        while not truck.truck_full() and len(priority_pkgs) != 0:
            nearest = __find_nearest_hub(priority_pkgs, truck.truck_location())
            depend_pkg = nearest.pkg_dependencies
            for pkg in depend_pkg:
                depend_pkg = depend_pkg.union(cast(set[PkgObject], pkg.pkg_dependencies))
            depend_pkg.add(nearest)
            if truck.truck_cap() >= len(depend_pkg):
                while len(depend_pkg) != 0:
                    pkg = __find_nearest_hub(depend_pkg, truck.truck_location())
                    depend_pkg.discard(pkg)
                    if not pkg.set_at_hub():
                        continue
                    priority_pkgs.discard(pkg)
                    truck.load_truck(pkg)
                    for k in (pkg_dest_table.get(pkg.address)) or []:
                        if not truck.truck_full() and k.pkg_delivery_eligibility(truck):
                            priority_pkgs.discard(k)
                            truck.load_truck(k)


def deliver_remainder_of_pkgs() -> int:
    """
    T(n) = O(n)
    S(n) = O(n)
    Used to deliver any remaining packages after priority packages have been delivered
    :param: None
    :return: int
    """
    pkg_lst = []
    for pkg in __PKGS_ALL:
        if pkg[1].set_at_hub():
            pkg_lst.append(pkg[1])

    sort_packages(pkg_lst)
    return route_trucks()


def distance_finder() -> DHGraph[Union[DeliveryHub, str]]:
    """
    T(n) = O(n**2)
    S(n) = O(n**2)
    Uses the distance chart provided for the project to build a graph by using the postal code and address
    as a unique identifier. This enables the delivery hub to searched for by either a string containing
    this information or the delivery hub object.
    :param: None
    :return Graph of Delivery Hubs:
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
    This method is responsible for determining the best way to deliver the packages
    :param: None
    :return: PKGS_ALL, TRUCKS
    """
    global __PKGS_ALL
    global __TRUCKS_ALL
    global __GRAPH
    __TRUCKS_ALL = [Truck(), Truck()]
    __PKGS_ALL, pkg_dest_table = pkg_importer()  # As defined above T(n) = O(n)
    __GRAPH = distance_finder()  # O(m**2) m is the number of hubs in the graph
    priority_pending_delivery = True
    while priority_pending_delivery:
        __priority_first(pkg_dest_table)
        if priority_pending_delivery := any([not truck.truck_empty() for truck in __TRUCKS_ALL]):
            deliver_remainder_of_pkgs()
    remaining_pkgs = sum(map(lambda x: 0 if x[1].pkg_is_delivered() else 1, __PKGS_ALL))
    while remaining_pkgs != 0:
        remaining_pkgs -= deliver_remainder_of_pkgs()
    return __PKGS_ALL, __TRUCKS_ALL

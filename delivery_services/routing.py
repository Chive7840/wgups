# External libraries
from truck import Truck
# Internal Modules
from delivery_hub import DeliveryHub
from delivery_services.pkg_handler import PkgObject
from data_services import DHGraph, HashTable
import csv
from typing import Iterable, Union, cast

pkgs_file = '../input_files/reformatted_package.csv'
distance_file = '../input_files/reformatted_dist.csv'

BASE = 'BASE'
time_at_base = 60 * 8

__TRUCKS_ALL: [Truck]
__PKGS_ALL: HashTable[int, PkgObject]
__GRAPH: DHGraph[Union[DeliveryHub, str]]

wrong_addr = None


def pkg_importer() -> tuple[HashTable[int, PkgObject], HashTable[str, list[PkgObject]]]:
    """
    T(n) = O(n)
    S(n) = O(n)
    :param: None
    :return: pkgs, pkg_dest
    """
    pkgs = HashTable[int, PkgObject]()
    pkg_dest = HashTable[str, list[PkgObject]]()
    dependency_lst = HashTable[int, set[PkgObject]]()

    with open(pkgs_file) as pkg_f:
        for row in csv.reader(pkg_f, delimiter=','):
            pkg = PkgObject(*row)
            pkgs.insert(pkg.pkg_id, pkg)
            if pkgs_lst := pkg_dest.get(pkg.addr) is None:
                pkgs_lst: list[PkgObject] = []
                pkg_dest.insert(pkg.addr, pkgs_lst)
            pkgs_lst.append(pkg)
            for dep_pkg in pkg.depend_pkg:
                if dep_pkgs := dependency_lst.get(dep_pkg) is None:
                    dep_pkgs = set()
                    dependency_lst.insert(dep_pkg, dep_pkgs)
                dep_pkgs.add(pkg)
            for __pkg in dependency_lst.get(pkg.pkg_id) or []:
                __pkg.next_pkg.add(pkg)
                pkg.next_pkg.add(__pkg)
    return pkgs, pkg_dest


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
        for truck in __TRUCKS_ALL:
            if truck.truck_full():
                continue
            __min = float('inf')
            nearest = None
            for pkg in pkgs:
                if pkg.pkg_delivery_eligibility(truck):
                    pkg_count += 1
                    distance = __GRAPH.get_distance(truck.truck_location(), pkg.addr)
                    if distance < __min:
                        __min = distance
                        nearest = pkg

            if nearest is not None:
                truck.load_truck(nearest)


def priority_first(pkg_dest: HashTable[str, list[PkgObject]]) -> None:
    """
    T(n): O(n)
    S(n): O(n)
    :param pkg_dest:
    :return: None
    """
    priority_pkgs = set([pkg[1] for pkg in __PKGS_ALL
                         if any([pkg[1].pkg_prioritizer(truck.get_time_elapsed())
                                 and pkg[1].pkg_delivery_eligibility(truck) for truck in __PKGS_ALL])])

    __TRUCKS_ALL.sort(key=lambda truck: truck.total_miles)

    for truck in __TRUCKS_ALL:

        while not truck.truck_full() and len(priority_pkgs) != 0:
            nearest = find_nearest_hub(priority_pkgs, truck.truck_location())
            depend_pkg = nearest.next_pkg
            for pkg in depend_pkg:
                depend_pkg = depend_pkg.union(cast(set[PkgObject], pkg.next_pkg))
            depend_pkg.add(nearest)
            if truck.truck_cap() > len(depend_pkg):
                while len(depend_pkg) != 0:
                    pkg = find_nearest_hub(depend_pkg, truck.truck_location())
                    depend_pkg.discard(pkg)
                    if not pkg.at_base():
                        continue
                    priority_pkgs.discard(pkg)
                    truck.load_truck(pkg)
                    for pkg in pkg_dest.get(pkg.addr) or []:
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
    non_priority_pkgs = [pkg[1] for pkg in __PKGS_ALL if pkg[1].at_base()]
    sort_packages(non_priority_pkgs)
    return route_trucks()


def delivery_scheduler() -> tuple[HashTable[int, PkgObject], list[Truck]]:
    """
    Assume:
    m = number of delivery hubs
    n = number of packages
        T(n) = O(m**2) + O(n)
        S(n) = O(m**2) + O(n)
    :param: None
    :return: __PKGS_ALL, __TRUCKS
    """
    global __PKGS_ALL
    global __TRUCKS_ALL
    global __GRAPH
    # O(n)
    __PKGS_ALL, pkg_dest = pkg_importer()
    __TRUCKS_ALL = [Truck(), Truck()]
    # O(m**2)
    __GRAPH = distance_finder()

    priority_pending_delivery = True
    while priority_pending_delivery:
        priority_first(pkg_dest)
        if priority_pending_delivery := any([not truck.truck_empty() for truck in __TRUCKS_ALL]):
            deliver_remainder_of_pkgs()

    remaining_pkgs = sum(map(lambda x: 0 if x[1].pkg_delivered() else 1, __PKGS_ALL))
    while remaining_pkgs != 0:
        remaining_pkgs -= deliver_remainder_of_pkgs()

    return __PKGS_ALL, __TRUCKS_ALL


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

        for dh_name, dh_addr, *distances in csv.reader(dist_f, delimiter=',', quotechar='"'):
            hub = DeliveryHub(dh_name, dh_addr)
            dh_graph.insert_vertex(hub)
            delivery_hubs.append(hub)
            for h, distance in enumerate(distances):
                dh_graph.insert_edge(hub, delivery_hubs[h], float(distance))
    return dh_graph


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
        distance = __GRAPH.get_distance(pkg.addr, location)
        if distance < min_dist:
            min_dist = distance
            next_nearest = pkg

    return cast(PkgObject, next_nearest)


def route_trucks() -> int:
    """
    T(n) = O(n)
    S(n) = O(1)
    :param: None
    :return: delivered int
    """
    global wrong_addr
    if wrong_addr is None:
        wrong_addr = [pkg[1] for pkg in __TRUCKS_ALL if pkg[1].wrong_address]

    delivered = 0

    for truck in __TRUCKS_ALL:
        delivered += len(truck.pkg_lst)
        truck.load_truck(__GRAPH)

        if len(wrong_addr) != 0:
            for pkg in wrong_addr:
                if pkg.address_correction_available(truck.get_truck_id()):
                    pkg.corrected_address()
                    wrong_addr.remove(pkg)
    return delivered

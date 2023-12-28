from delivery_services.routing import auto_router
from utilities import deadline_to_minutes, SOURCE_DIR
import unittest
import csv

from delivery_services.truck import Truck
from delivery_services.delivery_hub import DeliveryHub
from delivery_services.pkg_handler import PkgObject
from utilities import SOURCE_DIR
from data_services import DHGraph, HashTable
import csv
from typing import Iterable, Union, cast

now = deadline_to_minutes('11:00')
wgups_tst_one = SOURCE_DIR / 'test_services' / 'test_data' / 'big_o' / '__WGUPS_pkg_file_test_one.csv'
wgups_tst_two = SOURCE_DIR / 'test_services' / 'test_data' / 'big_o' / '__WGUPS_pkg_file_test_two.csv'
wgups_tst_three = SOURCE_DIR / 'test_services' / 'test_data' / 'big_o' / '__WGUPS_pkg_file_test_three.csv'
wgups_tst_four = SOURCE_DIR / 'test_services' / 'test_data' / 'big_o' / '__WGUPS_pkg_file_test_four.csv'
wgups_tst_five = SOURCE_DIR / 'test_services' / 'test_data' / 'big_o' / '__WGUPS_pkg_file_test_five.csv'
wgups_tst_six = SOURCE_DIR / 'test_services' / 'test_data' / 'big_o' / '__WGUPS_pkg_file_test_six.csv'
wgups_tst_seven = SOURCE_DIR / 'test_services' / 'test_data' / 'big_o' / '__WGUPS_pkg_file_test_seven.csv'
wgups_tst_eight = SOURCE_DIR / 'test_services' / 'test_data' / 'big_o' / '__WGUPS_pkg_file_test_eight.csv'
wgups_tst_nine = SOURCE_DIR / 'test_services' / 'test_data' / 'big_o' / '__WGUPS_pkg_file_test_nine.csv'
wgups_tst_ten = SOURCE_DIR / 'test_services' / 'test_data' / 'big_o' / '__WGUPS_pkg_file_test_ten.csv'

__wgups_pkgs = SOURCE_DIR / 'input_files' / '__WGUPS Package File.csv'
wgups_dists = SOURCE_DIR / 'input_files' / '__WGUPS Distance Table.csv'

class TestRouting(unittest.TestCase):
    def test_routing(self):
        # tst_pkgs, tst_trucks = auto_router()
        # tst_trucks.sort(key=lambda truck: truck.truck)
        # ichi_truck, ni_truck = tst_trucks
        # self.assertEqual(round(ichi_truck.total_miles, 1), 45.2)
        # self.assertEqual(round(ni_truck.total_miles, 1), 71.3)
        #
        # for (_, pkg) in tst_pkgs:
        #     print(pkg._PkgObject__get_pkg_information(now))
        #     if pkg._PkgObject__truck_tracker is not None:
        #         self.assertEqual(pkg._PkgObject__truck_tracker, pkg._PkgObject__delivered_by_truck)
        #         self.assertLessEqual(pkg.delivered_at_time, pkg.delivery_promise)
        #         self.assertLessEqual(pkg._PkgObject__available_when, pkg._PkgObject__truck_loaded_at_time)


        dh_graph = DHGraph[Union[DeliveryHub, str]]()
        with open(wgups_dists) as dist_f:
            delivery_hubs: list[DeliveryHub] = []
            hub_reader = csv.reader(dist_f, delimiter=';', quotechar='"')
            for dh_name, dh_addr, *dh_dists in hub_reader:
                hub = DeliveryHub(dh_name, dh_addr)
                dh_graph.insert_hub(hub)
                delivery_hubs.append(hub)
                for (h, dist) in enumerate(dh_dists):
                    dh_graph.insert_graph_edge(hub, delivery_hubs[h], float(dist))

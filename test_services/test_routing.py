from pathlib import Path
from delivery_services.routing import auto_router
from utilities import deadline_to_minutes
import unittest
from datetime import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)

now = deadline_to_minutes('11:30')
wgups_package = Path('../input_files/__WGUPS Package File.csv')
wgups_dist = Path('../input_files/__WGUPS Distance Table.csv')

class TestRouting(unittest.TestCase):
    def test_routing(self):
        tst_pkgs, tst_trucks = auto_router()
        tst_trucks.sort(key=lambda truck: truck.truck_number)
        ichi_truck, ni_truck = tst_trucks
        self.assertEqual(round(ichi_truck.total_miles, 1), 45.2)
        self.assertEqual(round(ni_truck.total_miles, 1), 72.2)

        for (_, pkg) in tst_pkgs:
            print(pkg._PkgObject__get_pkg_status(now))
            if pkg._PkgObject__truck_tracker is not None:
                self.assertEqual(pkg._PkgObject__truck_tracker, pkg._PkgObject__delivered_by_truck)
                self.assertLessEqual(pkg.delivered_at_time, pkg.delivery_promise)
                self.assertLessEqual(pkg._PkgObject__available_when, pkg._PkgObject__truck_loaded_at_time)




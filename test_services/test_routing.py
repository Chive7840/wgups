import re

from delivery_services.routing import auto_router
from delivery_services.delivery_hub import DeliveryHub
from data_services.graph import DHGraph
import utilities

from typing import Union, Match
import unittest
import random
import csv

from datetime import datetime
import pandas as pd
pd.set_option('display.max_columns', None)

now = datetime.now()
wgups_package = '../input_files/__WGUPS Package File.csv'
wgups_dist = '../input_files/__WGUPS Distance Table.csv'

class TestRouting(unittest.TestCase):
    def test_routing(self):
        tst_pkgs, tst_trucks = auto_router()
        tst_trucks.sort(key=lambda truck: truck.truck_number)
        ichi_truck, ni_truck = tst_trucks
        self.assertEqual(round(ichi_truck.total_miles, 1), 45.2)
        self.assertEqual(round(ni_truck.total_miles, 1), 71,3)




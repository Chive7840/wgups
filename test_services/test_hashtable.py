from data_services.hash_table import HashTable
from data_services.graph import DHGraph
import unittest


class TestHashTable(unittest.TestCase):
    def test_get_method(self):
        # Testing integer objects
        tst_hub = HashTable[object, object]()
        tst_hub.insert(3, 4)
        self.assertEqual(tst_hub.get(3), 4)
        tst_hub.insert(3, 5)
        self.assertEqual(tst_hub.get(3), 5)
        tst_hub.insert(28, 5)
        self.assertEqual(tst_hub.get(3), 5)
        self.assertEqual(tst_hub.get(28), 5)
        tst_hub.insert(38, 5)
        self.assertEqual(tst_hub.get(3), 5)
        self.assertEqual(tst_hub.get(28), 5)
        self.assertEqual(tst_hub.get(38), 5)
        tst_hub.insert(41, 5)
        self.assertEqual(tst_hub.get(3), 5)
        self.assertEqual(tst_hub.get(28), 5)
        self.assertEqual(tst_hub.get(38), 5)
        self.assertEqual(tst_hub.get(41), 5)

        # Testing string objects
        tst_hub.insert('test1', 'test2')
        self.assertEqual(tst_hub.get('test1'), 'test2')
        tst_hub.insert('test1', 'test4')
        self.assertEqual(tst_hub.get('test1'), 'test4')
        tst_hub.insert('test12', 'test4')
        self.assertEqual(tst_hub.get('test1'), 'test4')
        self.assertEqual(tst_hub.get('test12'), 'test4')

    def test_insert_method(self):
        tst_table = HashTable[int, int]()
        tst_table.insert(3, 4)
        self.assertEqual(tst_table.tbl_storage, [[], [(3, 4)]])
        self.assertEqual(tst_table.size, 1)
        tst_table.insert(3,  5)
        self.assertEqual(tst_table.tbl_storage, [[], [(3, 5)]])
        self.assertEqual(tst_table.size, 1)
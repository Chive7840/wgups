from data_services.graph import DHGraph
import unittest


class TestDHGraph(unittest.TestCase):
    def test_get_distance(self):
        tst_graph = DHGraph[str]()
        dh_a = 'Delivery Hub a'
        dh_b = 'Delivery Hub b'
        tst_graph.insert_hub(dh_a)
        tst_graph.insert_hub(dh_b)
        tst_graph.insert_graph_edge(dh_a, dh_b, 1.0)
        self.assertEqual(tst_graph.get_distance(dh_a, dh_b), 1.0)

    # Test results
    # with arguments python -m unittest
    #
    # Ran 1 test in 0.002s
    #
    # OK

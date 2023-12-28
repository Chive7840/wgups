from __future__ import annotations
import logging
from data_services.hash_table import HashTable
from utilities import SOURCE_DIR
from typing import TypeVar, Generic

# Creates a logger using the module name
logger = logging.getLogger(__name__)
# Specifies that only DEBUG level logs should be saved
logger.setLevel(logging.DEBUG)
# Specifies the name and path for the log file
graph_log_file = SOURCE_DIR / 'data_services' / 'data_logs' / 'graph.log'
graph_handler = logging.FileHandler(graph_log_file)
# Specifies a format for the logs being recorded
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
# Sets the handler's formatter
graph_handler.setFormatter(formatter)
# Adds the file handler to the logger
logger.addHandler(graph_handler)

obj_id = TypeVar('obj_id')


class DHGraph(Generic[obj_id]):
    graph_edge: HashTable[obj_id, HashTable[obj_id, float]] = HashTable()

    def insert_graph_edge(self, hub_a: obj_id, hub_b: obj_id, distance: float):
        self.__insert_graph_edge(hub_a, hub_b, distance)
        self.__insert_graph_edge(hub_b, hub_a, distance)

    def __insert_graph_edge(self, hub_a: obj_id, hub_b: obj_id, distance: float):
        self.graph_edge.fetch_bucket(hub_a).insert(hub_b, distance)

    def insert_hub(self, dh: obj_id):
        """
        Inserts an individual vertex into the graph
        :param dh:
        :return:
        """
        self.graph_edge.insert(dh, HashTable[obj_id, float]())

    def get_distance(self, hub_a: obj_id, hub_b: obj_id) -> float:
        """
        Returns the distance between the two provided delivery hub inputs
        :param hub_a:
        :param hub_b:
        :return Distance float value:
        """
        dist_edge = self.graph_edge.fetch_bucket(hub_a).fetch_bucket(hub_b)
        # logger.debug(f'Hub_A: {hub_a} Hub_B: {hub_b} Distance: {dist_edge}') #  Only enabled for troubleshooting
        return dist_edge

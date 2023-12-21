from __future__ import annotations
import logging
from data_services.hash_table import HashTable
from typing import TypeVar, Generic

# Creates a logger using the module name
logger = logging.getLogger(__name__)
# Specifies that only DEBUG level logs should be saved
logger.setLevel(logging.DEBUG)
# Specifies the name and path for the log file
graph_handler = logging.FileHandler('../data_services/data_logs/graph.log')
# Specifies a format for the logs being recorded
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
# Sets the handler's formatter
graph_handler.setFormatter(formatter)
# Adds the file handler to the logger
logger.addHandler(graph_handler)

T = TypeVar('T')


class DHGraph(Generic[T]):
    edge: HashTable[T, HashTable[T, float]] = HashTable()

    def insert_hub(self, dh: T) -> None:
        self.edge.insert(dh, HashTable[T, float]())

    def insert_edge(self, hub_a: T, hub_b: T, distance: float) -> None:
        # logger.info(f'Hub A: {hub_a}\tHub B: {hub_b}\tDistance: {distance}')  # TODO: REMOVE
        self.__insert_edge(hub_a, hub_b, distance)
        self.__insert_edge(hub_b, hub_a, distance)

    def __insert_edge(self, hub_a: T, hub_b: T, distance: float) -> None:
        self.edge.get(hub_a).insert(hub_b, distance)

    def get_distance(self, hub_a: T, hub_b: T) -> float:
        dist_edge = self.edge.get(hub_a).get(hub_b)
        logger.debug(f'Hub_A: {hub_a} Hub_B: {hub_b} Distance: {dist_edge}')
        return dist_edge

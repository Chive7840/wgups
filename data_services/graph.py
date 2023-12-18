from __future__ import annotations
from data_services.hash_table import HashTable
from typing import TypeVar, Generic

hub = TypeVar('hub')


class DHGraph(Generic[hub]):
    edges: HashTable[hub, HashTable[hub, float]] = HashTable()

    def insert_hub(self, dh: hub) -> None:
        self.edges.insert(dh, HashTable[hub, float]())

    def insert_edge(self, hub_a: hub, hub_b: hub, distance: float) -> None:
        self.__insert_edge(hub_a, hub_b, distance)
        self.__insert_edge(hub_b, hub_a, distance)

    def __insert_edge(self, hub_a: hub, hub_b: hub, distance: float) -> None:
        self.edges.get(hub_a).insert(hub_b, distance)

    def get_distance(self, hub_a: hub, hub_b: hub) -> float:
        return self.edges.get(hub_a).get(hub_b)
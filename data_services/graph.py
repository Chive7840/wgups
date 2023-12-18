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

    # TODO: Fix or remove
    # def search(self, curr_dh, destination_dh):  # Returns the distance for the provided delivery hubs
    #     return [h for i, h in self.route_weights.items() if i[0] == curr_dh and i[1] == destination_dh]
    #
    # def get_dh_by_index(self, index_val):
    #     return self.list_of_hubs[index_val]
    #
    # def get_dh_addr_by_id(self, dh_uid):
    #     for uid in range(len(self.list_of_hubs)):
    #         if self.list_of_hubs[uid].dh_id == dh_uid:
    #             return self.list_of_hubs[uid].dh_addr
    #
    # def get_dh_id_by_addr(self, address):
    #     for addr in range(len(self.list_of_hubs)):
    #         if self.list_of_hubs[addr].dh_addr == address:
    #             return self.list_of_hubs[addr].dh_id
    #         else:
    #             print("Invalid Address")


dh_graph = DHGraph()

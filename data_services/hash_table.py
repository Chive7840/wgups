from utilities import prime_num_gen
from typing import Generic, TypeVar, Optional

hsh_ind = TypeVar('hsh_ind')
hsh_val = TypeVar('hsh_val')


class HashTable(Generic[hsh_ind, hsh_val]):
    bucket_max = 2
    storage = list[list[tuple[hsh_ind, hsh_val]]]

    def __init__(self) -> None:
        self.prime_nums = prime_num_gen()
        self.starting_cap = next(self.prime_nums)
        self.set_storage()
        self.size = 0
        self.hash_table = []
        for x in range(self.starting_cap):
            self.hash_table.append([])

    def index_in_table(self, index: hsh_ind) -> bool:
        tmp_bucket = self.get_bucket(index)
        for k, _ in tmp_bucket:
            if k == index:
                return True
        return False

    def get_pkg_by_id(self, pkg_id: hsh_ind) -> Optional[hsh_val]:
        bkt_lst = self.get_bucket(pkg_id)
        for val in bkt_lst:
            if val[0] == pkg_id:
                return val[1]
        return None

    def get_bucket(self, index: hsh_ind) -> list[tuple[hsh_ind, hsh_val]]:
        bucket_index = hash(index) % self.starting_cap
        return self.storage[bucket_index]

    def get(self, index: hsh_ind) -> Optional[hsh_val]:
        for (bucket_ind, bucket_val) in self.get_bucket(index):
            if bucket_ind == index:
                return bucket_val

        return None

    def insert(self, index: hsh_ind, value: hsh_val) -> bool:
        tmp_lst = self.get_bucket(index)

        for (h, (i, _)) in enumerate(tmp_lst):
            if i == index:
                tmp_lst[h] = (index, value)
                break
        else:
            tmp_lst.append((index, value))
            self.size += 1

        if len(tmp_lst) > self.bucket_max:
            self.resize_table()
        return True

    def set_storage(self) -> None:
        self.storage = [[] for _ in range(self.size)]

    def resize_table(self) -> None:
        self.starting_cap = next(self.prime_nums)
        tmp_starting_cap = self.starting_cap

        for item in tmp_starting_cap:
            for i, v in item:
                self.insert(i, v)

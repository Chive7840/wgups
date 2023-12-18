from utilities import prime_num_gen
from typing import Generic, TypeVar, Optional

hsh_ind = TypeVar('hsh_ind')
hsh_val = TypeVar('hsh_val')


class HashTable(Generic[hsh_ind, hsh_val]):
    bucket_max = 2
    storage = list[list[tuple[hsh_ind, hsh_val]]]

    def __init__(self) -> None:
        self.__primes_generator = prime_num_gen()
        self.table_store_size = next(self.__primes_generator)
        self.set_storage()
        self.size = 0
        self.resize_option = True

    def insert(self, index: hsh_ind, value: hsh_val):
        tmp_lst = self.get_bucket(index)

        for (h, (i, _)) in enumerate(tmp_lst):
            if i == index:
                tmp_lst[h] = (index, value)
                break
        else:
            tmp_lst.append((index, value))
            if self.resize_option:
                self.size += 1

        if len(tmp_lst) > self.bucket_max:
            self.resize_table()

    def get_pkg_by_id(self, pkg_id: hsh_ind) -> Optional[hsh_val]:
        bkt_lst = self.get_bucket(pkg_id)
        for val in bkt_lst:
            if val[0] == pkg_id:
                return val[1]
        return None

    def get_bucket(self, index: hsh_ind) -> list[tuple[hsh_ind, hsh_val]]:
        bucket_index = hash(index) % self.table_store_size
        return self.storage[bucket_index]

    def get(self, index: hsh_ind) -> Optional[hsh_val]:
        for (bucket_ind, bucket_val) in self.get_bucket(index):
            if bucket_ind == index:
                return bucket_val

        return None

    def set_storage(self) -> None:
        self.storage = [[] for _ in range(self.table_store_size)]

    def resize_table(self) -> None:
        if not self.resize_option:
            return
        self.resize_option = False

        self.table_store_size = next(self.__primes_generator)
        old_size = self.storage
        self.set_storage()
        for item in old_size:
            for (k, v) in item:
                self.insert(k, v)

    # Dunder method for checking if a provided index input is valid
    def __contains__(self, index: hsh_ind) -> bool:
        tmp_bucket = self.get_bucket(index)
        for (k, _) in tmp_bucket:
            if k == index:
                return True
        return False

    def __iter__(self):
        for item in self.storage:
            yield from item
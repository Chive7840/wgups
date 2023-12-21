from utilities import prime_num_gen
from typing import Generic, TypeVar, Optional

hsh_ind = TypeVar('hsh_ind')
hsh_val = TypeVar('hsh_val')


class HashTable(Generic[hsh_ind, hsh_val]):
    bucket_max = 2
    __tbl_storage = list[list[tuple[hsh_ind, hsh_val]]]

    def __init__(self) -> None:
        self.primes_generator = prime_num_gen()
        self.table_store_size = next(self.primes_generator)
        self.set_storage()
        self.size = 0
        self.resize_option = True

    def insert(self, index: hsh_ind, value: hsh_val) -> None:
        tmp_lst = self.__get_bucket(index)

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

    def get(self, index: hsh_ind) -> Optional[hsh_val]:
        for (bucket_ind, bucket_val) in self.__get_bucket(index):
            if bucket_ind == index:
                return bucket_val
        return None

    def __get_bucket(self, index: hsh_ind) -> list[tuple[hsh_ind, hsh_val]]:
        bucket_index = hash(index) % self.table_store_size
        return self.__tbl_storage[bucket_index]

    def set_storage(self) -> None:
        self.__tbl_storage = [[] for _ in range(self.table_store_size)]

    def resize_table(self) -> None:
        if not self.resize_option:
            return
        self.resize_option = False

        self.table_store_size = next(self.primes_generator)
        old_size = self.__tbl_storage
        self.set_storage()
        for item in old_size:
            for (k, v) in item:
                self.insert(k, v)
        self.resize_option = True

    # Dunder method for checking if a provided index input is valid
    def __contains__(self, index: hsh_ind):
        tmp_bucket = self.__get_bucket(index)
        for (x, _) in tmp_bucket:
            if x == index:
                return True
        return False

    def __iter__(self):
        for item in self.__tbl_storage:
            yield from item


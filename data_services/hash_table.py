from utilities import prime_num_gen
from typing import Generic, TypeVar, Optional

hsh_ind = TypeVar('hsh_ind')
hsh_val = TypeVar('hsh_val')


class HashTable(Generic[hsh_ind, hsh_val]):
    bucket_max = 2
    __tbl_storage = list[list[tuple[hsh_ind, hsh_val]]]

    def __init__(self):
        self.primes_generator = prime_num_gen()
        self.tbl_storage_size = next(self.primes_generator)
        self.can_resize = True  # Used to flag when the hash table is able to resize
        self.init_storage()

        self.size = 0

    def insert(self, index: hsh_ind, value: hsh_val):
        """
        The method inserts new key value pairs into the table or updates existing keys
        :param index:
        :param value:
        :return:
        """
        tmp_lst = self.__fetch_bucket(index)

        for (h, (i, _)) in enumerate(tmp_lst):
            if i == index:
                tmp_lst[h] = (index, value)
                break
        else:
            tmp_lst.append((index, value))
            if self.can_resize:
                self.size += 1

        if len(tmp_lst) > self.bucket_max:
            self.resize_table()

    def get_bucket(self, index: hsh_ind) -> Optional[hsh_val]:
        """
        Returns a value if the hash index value matches the provided index
        :param index:
        :return Object or None:
        """
        for (bucket_ind, bucket_val) in self.__fetch_bucket(index):
            if bucket_ind == index:
                return bucket_val
        return None

    def __fetch_bucket(self, index: hsh_ind) -> list[tuple[hsh_ind, hsh_val]]:
        """
        Returns a list of values at the specified hash index location
        :param index:
        :return:
        """
        bucket_index = hash(index) % self.tbl_storage_size
        return self.__tbl_storage[bucket_index]

    def init_storage(self):
        self.__tbl_storage = [[] for _ in range(self.tbl_storage_size)]

    def resize_table(self):
        if not self.can_resize:
            return
        self.can_resize = False

        self.tbl_storage_size = next(self.primes_generator)
        prev_tbl_size = self.__tbl_storage
        self.init_storage()
        for item in prev_tbl_size:
            for (k, v) in item:
                self.insert(k, v)
        self.can_resize = True

    # Dunder method for checking if a provided index input is valid
    def __contains__(self, index: hsh_ind):
        tmp_bucket = self.__fetch_bucket(index)
        for (x, _) in tmp_bucket:
            if x == index:
                return True
        return False

    # Creates an iterator for the nested lists
    def __iter__(self):
        for item in self.__tbl_storage:
            yield from item


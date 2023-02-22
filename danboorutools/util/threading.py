from itertools import repeat
from multiprocessing import Value
from multiprocessing.pool import ThreadPool
from typing import Callable, TypeVar

ParallelItem = TypeVar("ParallelItem")
Args = TypeVar("Args")
ReturnTypeOfFunc = TypeVar("ReturnTypeOfFunc")


def run_in_parallel(function: Callable[[ParallelItem, Args], ReturnTypeOfFunc],
                    iterable: list[ParallelItem],
                    *arguments: Args,
                    threads: int = 4) -> None:
    """Run a list of iterables in a function, with extra arguments automatically iterated."""
    pool = ThreadPool(threads)
    iterating_arguments = [repeat(argument) for argument in arguments]
    pool.starmap(function, zip(iterable, *iterating_arguments))
    pool.close()


class Counter:
    def __init__(self, print_progress: bool = False) -> None:
        self.counter = Value('i', 0)
        self.print_progress = print_progress

    def __add__(self, other: int | float) -> "Counter":
        with self.counter.get_lock():
            self.counter.value += other  # type: ignore[attr-defined] # XXX False positive https://github.com/python/typeshed/issues/8799
            if self.print_progress:
                print(f"At {self.counter.value}...")  # type: ignore[attr-defined]
        return self

    def __sub__(self, other: int | float) -> "Counter":
        with self.counter.get_lock():
            self.counter.value -= other  # type: ignore[attr-defined]
            if self.print_progress:
                print(f"At {self.counter.value}...")  # type: ignore[attr-defined]
        return self

    def __str__(self) -> str:
        return str(self.counter.value)  # type: ignore[attr-defined]

    __iadd__ = __add__
    __isub__ = __sub__

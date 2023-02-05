from itertools import repeat
from multiprocessing import Value
from multiprocessing.pool import ThreadPool
from typing import Any, Callable, TypeVar

ParallelItem = TypeVar("ParallelItem")


def run_in_parallel(function: Callable[[ParallelItem], Any | None],
                    iterable: list[ParallelItem],
                    *arguments,
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
            self.counter.value += other  # type: ignore # XXX False positive https://github.com/python/typeshed/issues/8799
            if self.print_progress:
                print(f"At {self.counter.value}...")  # type: ignore
        return self

    def __sub__(self, other: int | float) -> "Counter":
        with self.counter.get_lock():
            self.counter.value -= other  # type: ignore
            if self.print_progress:
                print(f"At {self.counter.value}...")  # type: ignore
        return self

    def __str__(self) -> str:
        return str(self.counter.value)  # type: ignore

    __iadd__ = __add__
    __isub__ = __sub__

from .abstract import BuiltinAction
from dataclasses import dataclass, field
import mini_six.portable.win32.operation as operation
from typing import Callable
import time

__all__ = ["InArenaHallAction"]


@dataclass
class InArenaHallAction(BuiltinAction):
    close_arena_hall: Callable = field(init=False)

    def __post_init__(self):
        self.close_arena_hall = close_arena_hall_wrapper(self._handle)


def close_arena_hall_wrapper(hwnd):
    def close_arena_hall():
        operation.left_click(hwnd, 913, 42)

    return close_arena_hall

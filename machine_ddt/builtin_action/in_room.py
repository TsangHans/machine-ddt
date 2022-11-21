from .abstract import BuiltinAction
from dataclasses import dataclass, field
import mini_six.portable.win32.operation as operation
from typing import Callable
import time

__all__ = ["InRoomAction"]


@dataclass
class InRoomAction(BuiltinAction):
    start_game: Callable = field(init=False)
    open_bag: Callable = field(init=False)

    def __post_init__(self):
        self.start_game = start_game_wrapper(self._handle)
        self.open_bag = open_bag_wrapper(self._handle)


def start_game_wrapper(hwnd):
    def start_game():
        operation.left_click(hwnd, 940, 470)

    return start_game


def open_bag_wrapper(hwnd):
    def open_bag():
        operation.left_click(hwnd, 703, 564)

    return open_bag

from .abstract import BuiltinAction
from dataclasses import dataclass, field
import mini_six.portable.win32.operation as operation
from typing import Callable
import time

__all__ = ["InEntryAction"]


@dataclass
class InEntryAction(BuiltinAction):
    open_challenge_room: Callable = field(init=False)

    def __post_init__(self):
        self.open_challenge_room = open_challenge_room_wrapper(self._handle)


def open_challenge_room_wrapper(hwnd):
    def open_challenge_room():
        operation.left_click(hwnd, 641, 46)
        time.sleep(0.05)
        operation.left_click(hwnd, 769, 186)

    return open_challenge_room

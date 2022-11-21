from .abstract import BuiltinAction
from dataclasses import dataclass, field
import mini_six.portable.win32.operation as operation
from typing import Callable
import time

__all__ = ["InChallengeRoomAction"]


@dataclass
class InChallengeRoomAction(BuiltinAction):
    open_setting: Callable = field(init=False)
    quick_start: Callable = field(init=False)

    def __post_init__(self):
        self.open_setting = open_challenge_room_setting_wrapper(self._handle)
        self.quick_start = quick_start_wrapper(self._handle)


def open_challenge_room_setting_wrapper(hwnd):
    def open_challenge_room_setting():
        operation.left_click(hwnd, 721, 493)

    return open_challenge_room_setting


def quick_start_wrapper(hwnd):
    def quick_start():
        operation.left_click(hwnd, 545, 35)
        time.sleep(1)
        operation.left_click(hwnd, 948, 492)
        time.sleep(2)

    return quick_start

from dataclasses import dataclass, field
import time
from typing import Callable

import mini_six.portable.win32.operation as operation


@dataclass
class BuiltinAction:
    _handle: int


@dataclass
class InRoomAction(BuiltinAction):
    start_game: Callable = field(init=False)
    open_bag: Callable = field(init=False)

    def __post_init__(self):
        self.start_game = start_game_wrapper(self._handle)
        self.open_bag = open_bag_wrapper(self._handle)


@dataclass
class InGameAction(BuiltinAction):
    shoot: Callable = field(init=False)
    turn_left: Callable = field(init=False)
    turn_right: Callable = field(init=False)
    cancel_host: Callable = field(init=False)

    def __post_init__(self):
        self.shoot = shoot_wrapper(self._handle)
        self.turn_left = turn_left_wrapper(self._handle)
        self.turn_right = turn_right_wrapper(self._handle)
        self.cancel_host = cancel_host_wrapper(self._handle)


@dataclass
class RoomToGameAction(BuiltinAction):
    retire_exp: Callable = field(init=False)

    def __post_init__(self):
        self.retire_exp = retire_exp_wrapper(self._handle)


def shoot_wrapper(hwnd):
    def shoot(strength):
        during_time = (float(strength) + 1) * 40 / 1000
        operation.press_key(hwnd, operation.VK_SPACE)
        time.sleep(during_time)
        operation.release_key(hwnd, operation.VK_SPACE)

    return shoot


def turn_right_wrapper(hwnd):
    def turn_right():
        operation.click_key(hwnd, operation.VK_RIGHT)

    return turn_right


def turn_left_wrapper(hwnd):
    def turn_left():
        operation.click_key(hwnd, operation.VK_LEFT)

    return turn_left


def cancel_host_wrapper(hwnd):
    def cancel_host():
        operation.left_click(hwnd, 500, 240)

    return cancel_host


def start_game_wrapper(hwnd):
    def start_game():
        operation.left_click(hwnd, 940, 470)

    return start_game


def open_bag_wrapper(hwnd):
    def open_bag():
        operation.left_click(hwnd, 703, 564)

    return open_bag


def retire_exp_wrapper(hwnd):
    def retire_exp():
        pass

    return retire_exp

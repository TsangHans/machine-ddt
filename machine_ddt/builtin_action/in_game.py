from .abstract import BuiltinAction
from dataclasses import dataclass, field
import mini_six.portable.win32.operation as operation
from typing import Callable
import time

__all__ = ["InGameAction"]


@dataclass
class InGameAction(BuiltinAction):
    shoot: Callable = field(init=False)
    turn_left: Callable = field(init=False)
    turn_right: Callable = field(init=False)
    cancel_host: Callable = field(init=False)
    exit_game: Callable = field(init=False)

    def __post_init__(self):
        self.shoot = shoot_wrapper(self._handle)
        self.turn_left = turn_left_wrapper(self._handle)
        self.turn_right = turn_right_wrapper(self._handle)
        self.cancel_host = cancel_host_wrapper(self._handle)
        self.exit_game = exit_game_wrapper(self._handle)


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


def exit_game_wrapper(hwnd):
    def exit_game():
        operation.left_click(hwnd, 983, 11)
        time.sleep(0.05)
        operation.left_click(hwnd, 434, 349)

    return exit_game

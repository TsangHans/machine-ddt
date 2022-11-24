from machine_ddt.observer import get_panorama
from .abstract import BuiltinAction
from dataclasses import dataclass, field
import mini_six.portable.win32.operation as operation
from typing import Callable
import time

__all__ = ["InGameAction"]

from .. import DDTContextResource


@dataclass
class InGameAction(BuiltinAction):
    shoot: Callable = field(init=False)
    turn_left: Callable = field(init=False)
    turn_right: Callable = field(init=False)
    cancel_host: Callable = field(init=False)
    exit_game: Callable = field(init=False)
    get_panorama: Callable = field(init=False)
    pass_my_turn: Callable = field(init=False)
    update_players_ctx: Callable = field(init=False)

    def __post_init__(self):
        self.shoot = shoot_wrapper(self._handle)
        self.turn_left = turn_left_wrapper(self._handle)
        self.turn_right = turn_right_wrapper(self._handle)
        self.cancel_host = cancel_host_wrapper(self._handle)
        self.exit_game = exit_game_wrapper(self._handle, self._ctx)
        self.get_panorama = get_panorama_action_factory(self._handle)
        self.pass_my_turn = pass_my_turn_factory(self._handle)
        self.update_players_ctx = update_players_ctx_factory(self._handle, self._ctx)


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


def exit_game_wrapper(hwnd, ctx: DDTContextResource):
    def exit_game():
        operation.left_click(hwnd, 983, 11)
        time.sleep(0.05)
        operation.left_click(hwnd, 434, 349)
        ctx.players = list()  # 清空玩家信息

    return exit_game


def get_panorama_action_factory(hwnd):
    def get_panorama_action():
        panorama = get_panorama(hwnd, 1000, 600)

        return panorama

    return get_panorama_action


def pass_my_turn_factory(hwnd):
    def pass_my_turn():
        operation.click_key(hwnd, operation.VK_P)

    return pass_my_turn


def update_players_ctx_factory(hwnd: int, ctx: DDTContextResource):
    def update_players_ctx():
        # 1. 查找小地图玩家点的位置

        # 2. 将玩家点分为两类，分别进行操作
        #   （1）. 在无遮挡区域之内的：将玩家点移动到无遮挡区域内，使用血条检测
        #   （2）. 在无遮挡区域之外的：将玩家点移动到白框内，使用yolo检测

        # 3. 根据小地图白框相对位置和大地图的信息，综合得出玩家信息

        print("successfully works.")
        pass

    return update_players_ctx

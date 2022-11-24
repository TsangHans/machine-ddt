from .abstract import BuiltinAction
from dataclasses import dataclass, field
import mini_six.portable.win32.operation as operation
from typing import Callable
import time

__all__ = ["InChallengeRoomAction"]


@dataclass
class InChallengeRoomAction(BuiltinAction):
    select_map: Callable = field(init=False)
    quick_start: Callable = field(init=False)

    def __post_init__(self):
        self.select_map = select_map_wrapper(self._handle)
        self.quick_start = quick_start_wrapper(self._handle)


def open_challenge_room_setting(hwnd):
    operation.left_click(hwnd, 721, 493)


def confirm_challenge_room_setting(hwnd):
    operation.left_click(hwnd,500,525)


def select_map_wrapper(hwnd):
    block_position = (
        (285, 250), (420, 250), (555, 250), (690, 250),
        (285, 305), (420, 305), (555, 305), (690, 305),
        (285, 360), (420, 360), (555, 360), (690, 360),
    )

    def scroll_map_page(page_num):
        operation.left_down(hwnd, 775, 238)
        operation.move_to(hwnd, 775, 238 + int(page_num * 11.2))
        operation.left_up(hwnd, 775, 238)

    def select_map(map_id):
        open_challenge_room_setting(hwnd)
        time.sleep(1.5)

        if map_id < 0 or map_id > 122:
            raise ValueError("map_id should in 0 to 122.")

        # 一页 12 个地图
        page_id = map_id // 12  # 页号
        block_id = map_id % 12  # 块号
        scroll_map_page(page_id)
        if 0 <= page_id < 10:
            operation.left_click(hwnd, *block_position[block_id])
        elif page_id == 10:
            operation.left_click(hwnd, *block_position[block_id + 8])
        time.sleep(1.5)
        confirm_challenge_room_setting(hwnd)

    return select_map


def quick_start_wrapper(hwnd):
    def quick_start():
        operation.left_click(hwnd, 545, 35)
        time.sleep(1)
        operation.left_click(hwnd, 948, 492)
        time.sleep(2)

    return quick_start

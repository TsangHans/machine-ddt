from __future__ import annotations

from ctypes import byref, c_ubyte
from typing import Tuple

import numpy as np
import time

import mini_six.core as core
import mini_six.portable.win32.operation as operation
from mini_six.portable.win32.windll import (
    GetDC,
    CreateCompatibleDC,
    GetClientRect,
    CreateCompatibleBitmap,
    SetProcessDPIAware,
    SelectObject,
    BitBlt,
    GetBitmapBits,
    DeleteObject,
    ReleaseDC,
    RECT,
    SRCCOPY,
    SendMessageW,
    WM_ACTIVATE
)

__all__ = ["PanoramicScreenShot"]

SetProcessDPIAware()


def is_edge_factory(mask: np.ndarray, unit=5):
    """判断是不是边，unit 表示连续 5 个点才能算一条边"""
    height, width = mask.shape
    if height < unit or width < unit:
        raise ValueError(f"Unit={unit} is too large, try smaller one.")

    def is_edge(x, y):

        if not ((0 <= x < width) or (unit <= y < height)):
            raise ValueError(f"x={x}, y={y} is invalid index.")

        res_x = False
        if x >= unit:
            res_x = True
            for i in range(x + 1 - unit, x + 1):
                res_x = mask[y, i] and res_x
        if not res_x:
            if x <= width - unit:
                res_x = True
                for i in range(x, x + unit):
                    res_x = mask[y, i] and res_x

        res_y = False
        if not res_x:
            if y >= unit:
                res_y = True
                for j in range(y + 1 - unit, y + 1):
                    res_y = mask[j, x] and res_y
        if not res_y:
            if y <= height - unit:
                res_y = True
                for j in range(y, y + unit):
                    res_y = mask[j, x] and res_y

        res = res_x or res_y

        return res

    return np.vectorize(is_edge)


def get_small_map_pos(img: np.ndarray):
    """同时结合水平检测和垂直检测"""
    left_lim = 750  # 因为小地图右边，设置左边界过滤掉一些噪声

    r_mask_1 = (img[:, :, 0] >= 155) * (img[:, :, 0] <= 165)
    g_mask_1 = (img[:, :, 1] >= 155) * (img[:, :, 1] <= 165)
    b_mask_1 = (img[:, :, 2] >= 155) * (img[:, :, 2] <= 165)
    r_mask_2 = (img[:, :, 0] >= 230) * (img[:, :, 0] <= 255)
    g_mask_2 = (img[:, :, 1] >= 230) * (img[:, :, 1] <= 255)
    b_mask_2 = (img[:, :, 2] >= 230) * (img[:, :, 2] <= 255)
    mask_1 = r_mask_1 * g_mask_1 * b_mask_1  # 垂直检测
    mask_2 = r_mask_2 * g_mask_2 * b_mask_2  # 水平检测

    small_map_pos = None

    if not (np.sum(mask_1[: 120, left_lim:]) == 0 and np.sum(mask_2[: 120, left_lim:]) == 0):
        is_edge_vec_func_1 = is_edge_factory(mask_1[: 120, left_lim:], unit=10)
        is_edge_vec_func_2 = is_edge_factory(mask_2[: 120, left_lim:], unit=10)

        _y_1, _x_1 = np.where(mask_1[: 120, left_lim:])
        _y_2, _x_2 = np.where(mask_2[: 120, left_lim:])

        # 判断符合条件按的点可不可以成边
        edge_mask_1 = is_edge_vec_func_1(_x_1, _y_1)
        edge_mask_2 = is_edge_vec_func_2(_x_2, _y_2)

        edge_y_1, edge_x_1 = _y_1[edge_mask_1], _x_1[edge_mask_1]
        edge_y_2, edge_x_2 = _y_2[edge_mask_2], _x_2[edge_mask_2]

        # 只需确定小地图的 left 即可，其他都是确定的
        sm_left_1 = left_lim + min(edge_x_1)
        sm_left_2 = left_lim + min(edge_x_2) - 3

        # sm_left, sm_up, sm_right, sm_down = left_lim + min(edge_x_1), 24, 998, 120
        small_map_pos = max(sm_left_1, sm_left_2), 24, 998, 120

    return small_map_pos


def get_white_frame_pos(img: np.ndarray, small_map_pos: Tuple[int, int, int, int]):
    sm_left, sm_up, sm_right, sm_down = small_map_pos

    r_mask = img[:, :, 0] == 153
    g_mask = img[:, :, 1] == 153
    b_mask = img[:, :, 2] == 153
    mask = r_mask * g_mask * b_mask

    white_frame_pos = None

    if not np.sum(mask) == 0:
        is_edge_vec_func = is_edge_factory(mask[sm_up: sm_down, sm_left:sm_right])

        _y, _x = np.where(mask[sm_up: sm_down, sm_left:sm_right])

        edge_mask = is_edge_vec_func(_x, _y)

        edge_y, edge_x = _y[edge_mask], _x[edge_mask]

        white_frame_pos = sm_left + min(edge_x), sm_up + min(edge_y), sm_left + max(edge_x), sm_up + max(edge_y)

    return white_frame_pos


def one_shot(device_id, width, height):
    """单次截图"""
    _frame = bytearray(width * height * 4)
    _dc = GetDC(device_id)
    _cdc = CreateCompatibleDC(_dc)
    total_bytes = len(_frame)
    SendMessageW(device_id, WM_ACTIVATE, 1, 0)
    bitmap = CreateCompatibleBitmap(_dc, width, height)
    SelectObject(_cdc, bitmap)
    BitBlt(_cdc, 0, 0, width, height, _dc, 0, 0, SRCCOPY)
    byte_array = c_ubyte * total_bytes
    GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(_frame))
    DeleteObject(bitmap)
    image = np.frombuffer(_frame, dtype=np.uint8).reshape(height, width, 4)
    DeleteObject(_cdc)
    ReleaseDC(device_id, _dc)
    return image


def hide_or_show_interface(device_id):
    operation.left_down(device_id, 950, 460)
    operation.left_up(device_id, 950, 460)


def get_panorama(device_id, width, height):
    img_list = []

    img = one_shot(device_id, width, height)
    small_map_pos = get_small_map_pos(img)

    res = None

    if small_map_pos is not None:
        white_frame_pos = get_white_frame_pos(img, small_map_pos)
        if white_frame_pos is not None:
            sm_left, sm_up, sm_right, sm_down = small_map_pos
            wf_left, wf_up, wf_right, wf_down = white_frame_pos
            wf_width, wf_height = wf_right - wf_left, wf_down - wf_up

            width_convert = 1000 / wf_width
            height_convert = 600 / wf_height

            y_offset = wf_height

            touch_x, touch_y = int(wf_left + wf_width / 2), int(wf_up + wf_height / 2)
            dst_x, dst_y = sm_left, sm_up
            hide_or_show_interface(device_id)
            operation.left_down(device_id, touch_x, touch_y)
            operation.move_to(device_id, dst_x, dst_y)
            time.sleep(0.1)
            img = one_shot(device_id, width, height)
            operation.left_up(device_id, dst_x, dst_y)

            wf_left, wf_up, wf_right, wf_down = get_white_frame_pos(img, small_map_pos)
            # 1. 拽住白框移到小地图左上角，并截图
            while not ((sm_right - wf_right < 5) and (sm_down - wf_down < 5)):  # 终止条件：白框右下角坐标与小地图右下角坐标相等
                # 2. 计算移动的目的坐标，移动白框（平移，跳移），平移则横向拼接上一个图片，跳移则另起一个图片进行拼接，并截图
                if sm_right - 1 != wf_right:  # 行平移
                    x_offset = min(wf_width, sm_right - 1 - wf_right)
                    touch_x, touch_y = int(wf_left + wf_width / 2), int(wf_up + wf_height / 2)
                    operation.left_down(device_id, touch_x, touch_y)
                    dst_x = touch_x + x_offset
                    operation.move_to(device_id, dst_x, dst_y)
                    time.sleep(0.1)
                    n_img = one_shot(device_id, width, height)
                    operation.left_up(device_id, dst_x, dst_y)

                    t_img = n_img[int(600 - y_offset * height_convert):600,
                            int(1000 - (x_offset - 0.5) * width_convert):1000]
                    img = np.concatenate((img, t_img), axis=1)
                    wf_left, wf_up, wf_right, wf_down = wf_left + x_offset, wf_up, wf_right + x_offset, wf_down

                else:
                    img_list.append(img)
                    y_offset = min(wf_height, sm_down - 1 - wf_down)
                    touch_x, touch_y = int(wf_left + wf_width / 2), int(wf_up + wf_height / 2)
                    operation.left_down(device_id, touch_x, touch_y)
                    dst_x, dst_y = int(sm_left + wf_width / 2), touch_y + y_offset
                    operation.move_to(device_id, dst_x, dst_y)
                    time.sleep(0.08)
                    t_img = one_shot(device_id, width, height)
                    operation.left_up(device_id, dst_x, dst_y)
                    img = t_img[int(600 - y_offset * height_convert):600, :]
                    wf_left, wf_up, wf_right, wf_down = sm_left, wf_up + y_offset, sm_left + wf_width, wf_down + y_offset

            img_list.append(img)

            # 5. 把所有图片纵向拼接
            for i, img in enumerate(img_list):
                if i == 0:
                    res = img
                else:
                    try:
                        res = np.concatenate((res, img), axis=0)
                    except Exception as e:
                        res = None
                        break
            hide_or_show_interface(device_id)
    return res


class PanoramicScreenShot(core.Observer):
    def __init__(self, device_id: int):
        super().__init__(device_id)

        r = RECT()
        GetClientRect(device_id, byref(r))
        self._width, self._height = r.right, r.bottom

    def pull(self):
        panorama = get_panorama(self.device_id, self._width, self._height)
        return panorama

    def push(self):
        """实现全景截图"""
        image = self.pull()
        if image is not None:
            self.agent.notify(self, image)

from __future__ import annotations

from ctypes import byref, c_ubyte

import numpy as np

import mini_six.core as core
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


@core.Agent.register()
class PanoramicScreenShot(core.Observer):
    def __init__(self, device_id: int):
        super().__init__(device_id)
        r = RECT()
        GetClientRect(device_id, byref(r))
        self._width, self._height = r.right, r.bottom
        self._frame = bytearray(self._width * self._height * 4)

        self._dc = GetDC(device_id)
        self._cdc = CreateCompatibleDC(self._dc)

    def __del__(self):
        DeleteObject(self._cdc)
        ReleaseDC(self.device_id, self._dc)

    def one_shot(self):
        """单次截图"""
        total_bytes = len(self._frame)
        SendMessageW(self.device_id, WM_ACTIVATE, 1, 0)
        bitmap = CreateCompatibleBitmap(self._dc, self._width, self._height)
        SelectObject(self._cdc, bitmap)
        BitBlt(self._cdc, 0, 0, self._width, self._height, self._dc, 0, 0, SRCCOPY)
        byte_array = c_ubyte * total_bytes
        GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(self._frame))
        DeleteObject(bitmap)
        image = np.frombuffer(self._frame, dtype=np.uint8).reshape(self._height, self._width, 4)
        return image

    def run(self):
        """实现全景截图"""
        image = self.one_shot()
        self.agent.notify(self, image)

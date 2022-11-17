from enum import Enum

import win32gui
import re

__all__ = ["get_handle", "Handle"]


class Handle(Enum):
    HD_TG = 0
    HD_36 = 1


def get_handle(handle_type: Handle):
    if handle_type == Handle.HD_TG:
        hwnd = get_tg_hwnd()
    elif handle_type == Handle.HD_36:
        hwnd = get_36_hwnd()
    else:
        raise ValueError(f"Unexpected value Handle_type={handle_type}.")
    return hwnd


def get_tg_hwnd():
    windows_list = list()
    child_cls1 = "Afx:00400000:8:00010003:00000006:00000000"
    child_cls2 = "Shell Embedding"
    child_cls3 = "Shell DocObject View"
    child_cls4 = "Internet Explorer_Server"
    child_cls5 = "MacromediaFlashPlayerActiveX"

    hwnd_list = list()
    win32gui.EnumWindows(lambda hwnd, param: param.append(hwnd), windows_list)
    for window in windows_list:
        clsname = win32gui.GetClassName(window)  # 窗口类名
        if clsname == "Afx:00400000:8:00010003:00000006:00000000":
            # 第一层(window)
            child1 = win32gui.FindWindowEx(window, None, child_cls1, None)
            child2 = win32gui.FindWindowEx(child1, None, child_cls2, None)
            child3 = win32gui.FindWindowEx(child2, None, child_cls3, None)
            child4 = win32gui.FindWindowEx(child3, None, child_cls4, None)
            child5 = win32gui.FindWindowEx(child4, None, child_cls5, None)
            if child5 != 0:
                hwnd_list.append(child5)
    return hwnd_list


def get_36_hwnd():
    windows_list = list()
    title_list = list()
    hwnd_list = list()

    win32gui.EnumWindows(lambda hwnd, param: param.append(hwnd), windows_list)
    for window in windows_list:
        title = win32gui.GetWindowText(window)
        pattern = r'\|[0-9]+\|[0-9]+\|[0-9]+'
        if re.search(pattern, title): title_list.append(title)
    for title in title_list:
        hwnd = win32gui.FindWindow(0, title)
        hwnd1 = win32gui.GetDlgItem(hwnd, 0x78)
        hwnd2 = win32gui.GetDlgItem(hwnd1, 0xBE)
        hwnd3 = win32gui.GetDlgItem(hwnd2, 0x1)
        hwnd4 = win32gui.FindWindowEx(hwnd3, None, "MacromediaFlashPlayerActiveX", None)
        hwnd_list.append(hwnd4)

    return hwnd_list

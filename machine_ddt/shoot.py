import time
import mini_six.portable.win32.operation as operation


def shoot(hwnd, strength):
    during_time = (float(strength) + 1) * 40 / 1000
    operation.press_key(hwnd, operation.VK_SPACE)
    time.sleep(during_time)
    operation.release_key(hwnd, operation.VK_SPACE)

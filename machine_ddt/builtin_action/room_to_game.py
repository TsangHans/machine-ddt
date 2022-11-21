from .abstract import BuiltinAction
from dataclasses import dataclass, field
import mini_six.portable.win32.operation as operation
from typing import Callable
import time

__all__ = ["RoomToGameAction"]


@dataclass
class RoomToGameAction(BuiltinAction):
    retire_exp: Callable = field(init=False)

    def __post_init__(self):
        self.retire_exp = retire_exp_wrapper(self._handle)


def retire_exp_wrapper(hwnd):
    def retire_exp():
        pass

    return retire_exp

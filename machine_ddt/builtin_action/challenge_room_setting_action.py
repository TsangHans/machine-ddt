from .abstract import BuiltinAction
from dataclasses import dataclass, field
import mini_six.portable.win32.operation as operation
from typing import Callable
import time

__all__ = ["ChallengeRoomSettingAction"]


@dataclass
class ChallengeRoomSettingAction(BuiltinAction):
    scroll_map_page: Callable = field(init=False)

    def __post_init__(self):
        pass

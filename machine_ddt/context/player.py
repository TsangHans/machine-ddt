import enum
from typing import Tuple

from dataclasses import dataclass


class Identity(enum.Enum):
    ENEMY = 0
    TEAMMATE = 1


@dataclass
class Player:
    position: Tuple[Tuple[int, int], Tuple[int, int]]  # 表示头尾两个坐标，头尾的连线上的点为可命中的范围
    identity: Identity

from dataclasses import dataclass, field
from typing import List
from .player import Player


@dataclass(order=True)
class DDTContextResource:
    players: List[Player] = field(compare=False, default_factory=list)

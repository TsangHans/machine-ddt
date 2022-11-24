from dataclasses import dataclass
from machine_ddt.context import DDTContextResource

__all__ = ["BuiltinAction"]


@dataclass
class BuiltinAction:
    _handle: int
    _ctx: DDTContextResource

from dataclasses import dataclass
from typing import Dict, Callable

from machine_ddt.builtin_action import BuiltinAction, InRoomAction, InGameAction, \
    InChallengeRoomAction, InEntryAction, InArenaHallAction
from machine_ddt.builtin_observation import BuiltinObservation, InRoomObservation, InGameObservation, \
    InChallengeRoomObservation, InEntryObservation, InArenaHallObservation


@dataclass
class DDTData:
    custom_obs: Dict[str, str]
    custom_act: Dict[str, Callable]
    builtin_obs: BuiltinObservation
    builtin_act: BuiltinAction


@dataclass
class InRoomData(DDTData):
    builtin_obs: InRoomObservation
    builtin_act: InRoomAction


@dataclass
class InGameData(DDTData):
    builtin_obs: InGameObservation
    builtin_act: InGameAction


@dataclass
class RoomToGameData(DDTData):
    builtin_obs: InGameObservation
    builtin_act: InGameAction


@dataclass
class InChallengeRoomData(DDTData):
    builtin_obs: InChallengeRoomObservation
    builtin_act: InChallengeRoomAction


@dataclass
class InEntryData(DDTData):
    builtin_obs: InEntryObservation
    builtin_act: InEntryAction


@dataclass
class InArenaHallData(DDTData):
    builtin_obs: InArenaHallObservation
    builtin_act: InArenaHallAction

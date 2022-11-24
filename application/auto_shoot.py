import time

from machine_ddt import DDTAgent, Event, InGameData, InChallengeRoomData, DDTContextResource
from machine_ddt.data import InEntryData, InArenaHallData

ddt = DDTAgent()


@ddt.subscribe(Event.InGame)
def auto_shoot(data: InGameData, ctx: DDTContextResource):
    """自动射击"""
    data.builtin_act.update_players_ctx()

import asyncio

from machine_ddt import DDTAgent, Event, InGameData, InChallengeRoomData
from machine_ddt.data import InEntryData, InArenaHallData

ddt = DDTAgent()
ddt.init()


@ddt.coro_subscribe(Event.RoomToGame)
async def exit_game(data: InGameData):
    """定时退出游戏"""
    await asyncio.sleep(120)
    data.builtin_act.exit_game()


@ddt.subscribe(Event.InGame)
def in_game_cancel_host(data: InGameData):
    """取消托管"""
    if data.builtin_obs.host:
        data.builtin_act.cancel_host()


@ddt.subscribe(Event.InChallengeRoom)
def challenge_room_action(data: InChallengeRoomData):
    """快速开始挑战赛"""
    data.builtin_act.quick_start()


@ddt.subscribe(Event.InEntry)
def in_entry_action(data: InEntryData):
    """开启挑战赛房间"""
    data.builtin_act.open_challenge_room()


@ddt.subscribe(Event.InArenaHall)
def close_arena_window_action(data: InArenaHallData):
    """关闭竞技大厅窗口"""
    data.builtin_act.close_arena_hall()


ddt.run()

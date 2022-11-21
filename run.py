from machine_ddt import DDTAgent, Event, InRoomData, InGameData, RoomToGameData, InChallengeRoomData
from machine_ddt.data import InEntryData, InArenaHallData

ddt = DDTAgent()
ddt.init()


# @ddt.coro_subscribe(Event.InRoom)
# async def prepare_coro(data: InRoomData):
#     pass


# @ddt.subscribe(Event.InRoom)
# def prepare(data: InRoomData):
#     pass


@ddt.subscribe(Event.InGame)
def game_policy(data: InGameData):
    if data.builtin_obs.my_turn:
        data.builtin_act.turn_right()
        data.builtin_act.shoot(58.5)
    # print("wind: ", data.builtin_obs.wind)
    # print("angle: ", data.builtin_obs.angle)
    # if data.builtin_obs.host:
    #     data.builtin_act.cancel_host()
    # if data.builtin_obs.my_turn:
    #     data.builtin_act.turn_right()
    #     data.builtin_act.shoot(50)


# @ddt.subscribe(Event.RoomToGame)
# def some_policy(data: RoomToGameData):
#     data.builtin_act.retire_exp()

@ddt.subscribe(Event.InChallengeRoom)
def challenge_room_action(data: InChallengeRoomData):
    data.builtin_act.open_setting()


@ddt.subscribe(Event.InEntry)
def in_entry_action(data: InEntryData):
    pass


@ddt.subscribe(Event.InArenaHall)
def in_entry_action(data: InArenaHallData):
    data.builtin_act.close_arena_hall()


ddt.run()

from machine_ddt import DDTAgent, Event, InRoomData, InGameData, RoomToGameData

ddt = DDTAgent()
ddt.init()


@ddt.coro_subscribe(Event.InRoom)
async def prepare_coro(data: InRoomData):
    pass


# @ddt.subscribe(Event.InRoom)
# def prepare(data: InRoomData):
#     pass


@ddt.subscribe(Event.InGame)
def game_policy(data: InGameData):
    print("wind: ", data.builtin_obs.wind)
    print("angle: ", data.builtin_obs.angle)
    if data.builtin_obs.host:
        data.builtin_act.cancel_host()
    if data.builtin_obs.my_turn:
        data.builtin_act.turn_right()
        data.builtin_act.shoot(50)


@ddt.subscribe(Event.RoomToGame)
def some_policy(data: RoomToGameData):
    data.builtin_act.retire_exp()


ddt.run()

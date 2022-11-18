from machine_ddt import DDTAgent, Event, DDTData
from machine_ddt.shoot import shoot

ddt = DDTAgent()
ddt.init()


@ddt.subscribe(Event.InRoom)
def prepare(data: DDTData):
    if not data.observation["ready"]:
        data.action["start_game_delay"]()


@ddt.subscribe(Event.InGame)
def game_policy(data: DDTData):
    if data.observation["my_turn"]:
        data.action["toward_right"]()
        s


@ddt.subscribe(Event.RoomToGame)
def some_policy(data: DDTData):
    print("游戏开始")


ddt.run()

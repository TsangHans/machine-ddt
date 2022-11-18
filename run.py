from machine_ddt import DDTAgent, Event, DDTData

ddt = DDTAgent()
ddt.init()


@ddt.subscribe(Event.InRoom)
def prepare(data: DDTData):
    if not data.observation["ready"]:
        data.action["start_game_delay"]()


@ddt.subscribe(Event.InGame)
def game_policy(data: DDTData):
    print(data)


@ddt.subscribe(Event.RoomToGame)
def some_policy(data: DDTData):
    print("游戏开始")


ddt.run()

"""
运行 example 下的文件时，请确保工作路径下有 static 文件夹
"""

from machine_ddt import DDTAgent, Event, DDTData

ddt = DDTAgent()
ddt.init()


@ddt.subscribe(Event.InRoom)
def open_bag(data: DDTData):
    if data.observation["bag_available"]:
        data.action["open_bag"]()


ddt.run()

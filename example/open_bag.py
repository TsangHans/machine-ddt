"""
请在项目根目录运行 example 下的文件
"""
import sys
import os

sys.path.append(os.getcwd())
# 当你用 pycharm 的 run 和 debug 运行这个文件时，上面几行可以删掉

import machine_ddt as md

ddt = md.DDTAgent()
ddt.init()


@ddt.subscribe(md.Event.InRoom)
def open_bag(data: md.DDTData):
    if data.observation["bag_available"]:
        data.action["open_bag"]()


ddt.run()

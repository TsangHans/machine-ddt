# Machine-DDT Cookbook


## 准备食材
通过定义`yml`文件来定义你可以看到什么，可以做点什么，下面以`in_room_event.yml`为例来简述：
```yaml
# in_room_event.yml 即本文件，与 InRoom 事件绑定（每个 yml 文件与一个事件绑定，事件和 yml 文件名的映射关系由代码写死）
# analyze 项用于定义如何触发该事件
# 目前只支持：
#   1. InRoom（在竞技房间中）<-> in_room_event.yml
#   2. InGame（在竞技游戏中）<-> in_game_event.yml
analyze:
  position:  # left, up, right, bottom
    - 776
    - 12
    - 822
    - 36
  method: static_compare
  method_param:
    compare_image_fp: "image/in_room.png"

# observation 项用于定义你可以看到一些什么，该项内部分内容可自定义
observation:
  # 该自定义项 ready 表示观测准备按钮
  ready: # 可自定义
    # position 表示该 ready 图标的范围，用 left, up, right, bottom 坐标表示
    position: # 固定参数名
      - 929
      - 514
      - 983
      - 529
    # status 表示 ready 图标的状态，这里定义 no 为没有准备，yes 为已经准备
    status: # 固定参数名
      - no
      - yes
    # method 表示如何识别该自定义项的状态
    method: static_compare  # 固定参数名
    # 使用 static_compare 将定义 compare_image_fp 参数，传入 2 张与 ready 图标相同大小的图片，依次对应 ready 的两种状态
    method_param:
      compare_image_fp:
        - "image/in_room_ready.png"
        - "image/in_room_start.png"

  # 原理同上，可尝试自行理解
  bag_available:
    position:
      - 688
      - 550
      - 719
      - 579
    method: static_compare
    status:
      - yes
      - no
    method_param:
      compare_image_fp:
        - "image/in_room_bag_available.png"
        - "image/in_room_bag_not_available.png"

# action 项用于定义你可以做些什么，该项内部分内容可自定义
action:
  # 该自定义项 start_game 表示开始游戏这个动作
  start_game:  # 可自定义
    # method 定义完成该动作所需的内置函数，内置函数由本框架提供
    method: left_click  # 固定参数名
    # 如果使用 left_click，则需要传入点击的 (x, y) 坐标
    param:   # 固定参数名
      - 940
      - 470

  # 原理同上，可尝试自行理解
  open_bag:
    method: left_click
    param:
      - 703
      - 564

```
## 开始炒菜？
在准备好你想看到的图标（`observation`） 和 你可以做的动作（`action`）之后，就可以开始具体操作了。
这里以 `example/open_bag.py` 为例
```python
"""
运行 example 下的文件时，请确保工作路径下有 static 文件夹
"""

from machine_ddt import DDTAgent, Event, DDTData

"""
你可以先不用管这两行干什么用的，但是要记住这两行要在定义 @ddt.subscribe 这类函数之前。
特别是不要忘记 ddt.init()
"""
ddt = DDTAgent()
ddt.init()


"""
用 @ddt.subscribe(事件) 来订阅一个事件内容，内容通过形参（open_bag 函数的 data 参数）接收，
内容包括：
1. observation：你能看到的东西
2. action：你能做的动作
没错，就是我们刚刚在 yml 文件里自定义的那些东西。 
"""
@ddt.subscribe(Event.InRoom)
def open_bag(data: DDTData):
    # 背包能否被打开
    if data.observation["bag_available"]: 
        # 如果可以，那么就打开背包
        data.action["open_bag"]()

"""
在一切操作都定义完毕后，调用 ddt.run() 方法，将会开始无穷无尽的循环，即：
这行以下的代码都不会执行
"""
ddt.run()

```

import mini_six as six
from mini_six import SubscribeData, Config, DataSourceType, subscribe, load_plugin
from mini_six.portable.win32.observer import ScreenshotObserver

from machine_ddt.context.player import Player
import time
import enum
import logging
from . import logger

from .abstract import SingleMeta
from .handle import Handle, get_handle
from .context import DDTContextResource

from dataclasses import dataclass, field
from typing import Callable, Dict

config = Config()
config.add({"threshold": 0.5, "static": "static/ddt"})
ddt_logger = logging.getLogger("ddt")


class Event(enum.Enum):
    InGame = 0
    InRoom = 1
    RoomToGame = 2
    InChallengeRoom = 3
    InEntry = 4
    InArenaHall = 5


@dataclass(order=True)
class Action:
    priority: int
    call: Callable = field(compare=False)


def use_application(app_dir, app_name):
    load_plugin(app_dir, app_name)


class DDTAgent(metaclass=SingleMeta):
    def __init__(self):
        self._handles = get_handle(Handle.HD_TG)
        self._data_source = subscribe({DataSourceType.IMAGE: ScreenshotObserver}, self._handles)
        self._ctx: Dict[int, DDTContextResource] = {_handle: DDTContextResource() for _handle in self._handles}

        self._event_dict = {
            Event.InEntry: InEntry(ctx=self._ctx),
            Event.InGame: InGame(ctx=self._ctx),
            Event.InRoom: InRoom(ctx=self._ctx),
            Event.InChallengeRoom: InChallengeRoom(ctx=self._ctx),
            Event.InArenaHall: InArenaHall(ctx=self._ctx),
        }

        self._action_dict = {}
        self._last_event = None

    def init(self):

        # 对 PULL 订阅模式下的 action 进行优先级排序
        for _event in self._action_dict:
            self._action_dict[_event] = sorted(self._action_dict[_event])

        @self._data_source(priority=1)
        def ddt_publisher(data: SubscribeData):
            ctx = self._ctx.get(data.handle, None)

            similarity_list = []

            for _event_type, _event in self._event_dict.items():
                similarity = _event.analyze(data.image)
                similarity_list.append((similarity, _event_type))

            similarity_list = sorted(similarity_list, key=lambda i: i[0])

            poss_event = similarity_list[-1]
            if poss_event[0] >= config.get("threshold"):
                _event = poss_event[1]
                ddt_data = self._event_dict[_event].pull(data)
                self.notify(_event, ddt_data, ctx)

                if self._last_event in (Event.InRoom, Event.InChallengeRoom) and _event == Event.InGame:
                    self.notify(Event.RoomToGame, ddt_data, ctx)
                self._last_event = _event

        ddt_logger.info("@start-up DDT connect to six successfully.")

    def subscribe(self, _event: Event, priority: int = 1):
        def _decorator(func):

            action = Action(priority=priority, call=func)

            if _event in self._action_dict:
                self._action_dict[_event].append(action)
            else:
                self._action_dict[_event] = []
                self._action_dict[_event].append(action)
            ddt_logger.info(f"@start-up Action [{func.__name__}] has subscribed successfully.")
            return func

        return _decorator

    def notify(self, _event: Event, data, ctx: DDTContextResource):
        if _event in self._action_dict:
            for action in self._action_dict[_event]:
                action.call(data, ctx)
                ddt_logger.info(
                    f"@act-done Action [{action.call.__name__}] react to event [{_event}] successfully.")

    def run(self):
        ddt_logger.info(f"@start-up Scheduler is working...")
        six.run()


from .event import _DDTEvent, InGame, InRoom, InChallengeRoom, InRoomData, InGameData, RoomToGameData, InEntryData, \
    InChallengeRoomData, InEntry, InArenaHall

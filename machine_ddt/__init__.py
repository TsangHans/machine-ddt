import mini_six as six
from mini_six import look, DataSource, SubscribeMode, Config, Image

config = Config()
config.add({"threshold": 0.6, "static": "static/ddt"})

import time
import enum
import os
import logging
import sched
import threading
from . import logger

from .abstract import SingleMeta
from .handle import Handle, get_handle
from .observer import PanoramicScreenShot


class Event(enum.Enum):
    InGame = 0
    InRoom = 1
    RoomToGame = 2


six_logger = logging.getLogger("six")
ddt_logger = logging.getLogger("ddt")
for handler in six_logger.handlers:
    if not isinstance(handler, logging.FileHandler):
        handler.setLevel(logging.ERROR)
ddt_logger.setLevel(logging.INFO)

_scheduler = sched.scheduler()


def loop():
    time.sleep(config.get("clock"))
    _scheduler.enter(10, 10, loop)


_scheduler.enter(10, 10, loop)

_scheduler_task_list = []


class DDTAgent(metaclass=SingleMeta):
    def __init__(self):
        self._action_dict = {}
        self._event_dict = {
            Event.InGame: InGame(),
            Event.InRoom: InRoom()
        }
        self._last_event = None

    def init(self):
        six.init()

        handles = get_handle(Handle.HD_TG)

        @look(DataSource.SCREENSHOT, handles, period=1, priority=1, subscribe_mode=SubscribeMode.PULL)
        def ddt_publisher(data: Image):
            similarity_list = []

            for _event_type, _event in self._event_dict.items():
                similarity = _event.analyze(data.data)
                similarity_list.append((similarity, _event_type))

            similarity_list = sorted(similarity_list, key=lambda i: i[0])

            poss_event = similarity_list[-1]
            if poss_event[0] >= config.get("threshold"):
                _event = poss_event[1]
                data = self._event_dict[_event].pull(data)
                self.notify(_event, data)

                if self._last_event == Event.InRoom and _event == Event.InGame:
                    self.notify(Event.RoomToGame, data)
                self._last_event = _event

        ddt_logger.info("@start-up DDT connect to six successfully.")

    def subscribe(self, _event: Event, priority: int = 1):
        def _decorator(func):

            if _event in self._action_dict:
                self._action_dict[_event].append(func)
            else:
                self._action_dict[_event] = []
                self._action_dict[_event].append(func)
            ddt_logger.info(f"@start-up Action [{func.__name__}] has subscribed successfully.")
            return func

        return _decorator

    def notify(self, _event: Event, data):
        for action in self._action_dict[_event]:
            action(data)
            ddt_logger.info(
                f"@act-done Action [{action.__name__}] react to event [{_event}] successfully.")

    def run(self):
        t = threading.Thread(name="ddt_scheduler", target=_scheduler.run, daemon=True)
        t.start()
        ddt_logger.info(f"@start-up Scheduler is working...")
        six.run()


from .event import _DDTEvent, InGame, InRoom, InRoomData, InGameData, RoomToGameData

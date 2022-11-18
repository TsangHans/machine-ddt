from dataclasses import dataclass
from typing import Dict, Callable, Sized

import os
import machine_ddt
import mini_six.portable.win32.operation as operation

from mini_six import Config, Image
from machine_ddt import _scheduler, _scheduler_task_list
from machine_ddt.builtin_observation import BuiltinObservation, InGameObservation, InRoomObservation, \
    RoomToGameObservation
from machine_ddt.builtin_action import BuiltinAction, InGameAction, InRoomAction, RoomToGameAction
from machine_ddt.observe_method import onnx_recognize
from machine_ddt.key_map import KEY_MAP
import numpy as np
import cv2 as cv

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

__all__ = ["InGame", "InRoom", "InRoomData", "InGameData", "RoomToGameData"]

__module_path__ = machine_ddt.__file__.replace("\\__init__.py", "")

config = Config()


@dataclass
class DDTData:
    custom_obs: Dict[str, str]
    custom_act: Dict[str, Callable]


@dataclass
class InRoomData(DDTData):
    builtin_obs: InRoomObservation
    builtin_act: InRoomAction


@dataclass
class InGameData(DDTData):
    builtin_obs: InGameObservation
    builtin_act: InGameAction


@dataclass
class RoomToGameData(DDTData):
    builtin_obs: RoomToGameObservation
    builtin_act: RoomToGameAction


class _DDTEvent:
    def __init__(self, config_fp=None):
        self.analyze_config = {}
        self.observation_config = {}
        self.action_config = {}
        if config_fp is not None:
            self.load_config(config_fp)

        # self._agent = DDTAgent()

    def load_config(self, config_fp):
        """加载配置文件"""
        with open(config_fp, "r") as fr:
            conf = yaml.load(fr, Loader=Loader)
        self.analyze_config = conf["analyze"]
        self.observation_config = conf["observation"]
        self.action_config = conf["action"]

    @staticmethod
    def static_compare(origin_image: np.ndarray, compare_image: np.ndarray):
        similarity = np.sum(origin_image == compare_image) / origin_image.size
        return similarity

    def analyze(self, image: np.ndarray):
        """根据截图分析得出属于该状态的概率"""
        raise NotImplementedError("Please reload this method.")

    def get_builtin_observation(self, image: np.ndarray) -> BuiltinObservation:
        raise NotImplementedError("Please reload this method.")

    def get_builtin_action(self, _handle: int) -> BuiltinAction:
        raise NotImplementedError("Please reload this method.")

    def get_custom_observation(self, image: np.ndarray):
        obs = {}

        for observation, observation_config in self.observation_config.items():

            left, up, right, down = observation_config["position"]

            if "channel" in observation_config:
                channel = observation_config["channel"]
            else:
                channel = None

            cut_image = image[up:down, left:right, :]
            analyze_method = observation_config["method"]

            if analyze_method == "static_compare":
                method_param = observation_config["method_param"]
                compare_image_fp_iter = method_param["compare_image_fp"]
                status_iter = observation_config["status"]

                status_value_list = []

                for status, compare_image_fp in zip(status_iter, compare_image_fp_iter):
                    compare_image = cv.imread(os.path.join(config.get("static"), compare_image_fp))
                    similarity = self.static_compare(cut_image, compare_image)
                    status_value_list.append((similarity, status))

                prob, status = sorted(status_value_list, key=lambda i: i[0])[-1]
                if prob >= config.get("threshold"):
                    obs[observation] = status
                else:
                    obs[observation] = None

            elif analyze_method == "onnx_rec":  # 没有状态，识别的结果就是状态

                method_param = observation_config["method_param"]
                algorithm = method_param["algorithm"]
                onnx_model_fp = os.path.join(config.get("static"), method_param["onnx_model"])
                character_dict_fp = os.path.join(config.get("static"), method_param["character_dict"])
                input_image_shape = (3, down - up, right - left)

                res = onnx_recognize(cut_image, onnx_model_fp, character_dict_fp, input_image_shape, algorithm)

                obs[observation] = res

            elif analyze_method == "equal":
                channel_dim = 3
                if channel is not None:
                    channel_dim = len(channel)

                method_param = observation_config["method_param"]
                status_iter = observation_config["status"]
                compare_value_iter = method_param["compare_value"]

                status = None

                for s, compare_value in zip(status_iter, compare_value_iter):
                    if isinstance(compare_value, int):
                        value_dim = 1
                        compare_value = [compare_value]
                    elif isinstance(compare_value, Sized):
                        value_dim = len(compare_value)
                    else:
                        raise TypeError("Value type should be int or sized.")

                    if channel_dim != value_dim:
                        raise ValueError(f"Channel dim should be equal to value dim, now {channel_dim} != {value_dim}")

                    res = True
                    for c, v in zip(channel, compare_value):
                        res = res and cut_image[:, :, c] == v

                    if res:
                        status = s

                obs[observation] = status

            else:
                raise ValueError(f"Unexpected value analyze_method={analyze_method}.")

    def get_custom_action(self, _handle: int):
        act = {}
        for action, action_config in self.action_config.items():
            act[action] = {}
            method = action_config["method"]
            if method == "left_click":
                def func():
                    return operation.left_click(_handle, *action_config["param"])

                act[action] = func

            elif method == "click_key":
                def func():
                    for key in action_config["param"]:
                        if key not in KEY_MAP:
                            raise ValueError(f"Unexpected value key={key}.")

                        operation.click_key(_handle, KEY_MAP[key])

                act[action] = func

            elif method == "press_key":
                def func():
                    for key in action_config["param"]:
                        if key not in KEY_MAP:
                            raise ValueError(f"Unexpected value key={key}.")

                        operation.press_key(_handle, KEY_MAP[key])

                act[action] = func

            elif method == "release_key":
                def func():
                    for key in action_config["param"]:
                        if key not in KEY_MAP:
                            raise ValueError(f"Unexpected value key={key}.")

                        operation.release_key(_handle, KEY_MAP[key])

                act[action] = func

            elif method == "left_click_delay":
                delay = action_config["delay"]
                priority = action_config["priority"]

                scheduler_task_name = f"{str(self)}.{action}"

                def func():
                    if scheduler_task_name not in _scheduler_task_list:
                        _scheduler_task_list.append(f"{str(self)}.{action}")
                        _scheduler.enter(delay, priority, operation.left_click,
                                         argument=(_handle, *action_config["param"]))

                act[action] = func
        return act

    def pull(self, data: Image):
        """拉取该状态下所有信息"""
        image, _handle = data.data, data.handle

        if image.shape[2] == 4:
            image = image[:, :, :3]

        custom_obs = self.get_custom_observation(image)

        custom_act = self.get_custom_action(_handle)

        data = DDTData(custom_obs=custom_obs, custom_act=custom_act)

        return data


class InEntry:
    """在入口"""
    pass


class InRoom(_DDTEvent):
    """在房间"""

    def analyze(self, image: np.ndarray):
        if image.shape[2] == 4:
            image = image[:, :, :3]

        left, up, right, down = 776, 12, 822, 36
        cut_image = image[up:down, left:right, :]

        compare_image_fp = os.path.join(__module_path__, "static/image/in_room.png")
        compare_image = cv.imread(compare_image_fp)
        similarity = self.static_compare(cut_image, compare_image)
        return similarity

    def get_builtin_observation(self, image: np.ndarray) -> InRoomObservation:
        return InRoomObservation(_image=image)

    def get_builtin_action(self, _handle: int) -> InRoomAction:
        return InRoomAction(_handle=_handle)

    def pull(self, data: Image) -> InRoomData:
        custom_data = super().pull(data)

        image, _handle = data.data, data.handle

        if image.shape[2] == 4:
            image = image[:, :, :3]

        builtin_observation = self.get_builtin_observation(image)
        builtin_action = self.get_builtin_action(_handle)

        res = InRoomData(builtin_obs=builtin_observation, builtin_act=builtin_action,
                         custom_obs=custom_data.custom_obs,
                         custom_act=custom_data.custom_act)
        return res


class InGame(_DDTEvent):
    """在游戏"""

    def analyze(self, image: np.ndarray):
        if image.shape[2] == 4:
            image = image[:, :, :3]

        left, up, right, down = 974, 5, 993, 21
        cut_image = image[up:down, left:right, :]
        compare_image_fp = os.path.join(__module_path__, "static/image/in_game.png")
        compare_image = cv.imread(compare_image_fp)
        similarity = self.static_compare(cut_image, compare_image)
        return similarity

    def get_builtin_observation(self, image: np.ndarray) -> InGameObservation:
        obs = InGameObservation(_image=image)
        return obs

    def get_builtin_action(self, _handle: int) -> InGameAction:
        act = InGameAction(_handle=_handle)
        return act

    def pull(self, data: Image) -> InGameData:
        custom_data = super().pull(data)

        image, _handle = data.data, data.handle

        if image.shape[2] == 4:
            image = image[:, :, :3]

        builtin_observation = self.get_builtin_observation(image)
        builtin_action = self.get_builtin_action(_handle)

        res = InGameData(builtin_obs=builtin_observation, builtin_act=builtin_action, custom_obs=custom_data.custom_obs,
                         custom_act=custom_data.custom_act)
        return res


class RoomToGame(_DDTEvent):
    """由房间进入游戏"""

    def analyze(self, image: np.ndarray):
        return 0

    def get_builtin_observation(self, image: np.ndarray) -> RoomToGameObservation:
        return RoomToGameObservation(_image=image)

    def get_builtin_action(self, _handle: int) -> RoomToGameAction:
        return RoomToGameAction(_handle=_handle)

    def pull(self, data: Image) -> RoomToGameData:
        custom_data = super().pull(data)

        image, _handle = data.data, data.handle

        if image.shape[2] == 4:
            image = image[:, :, :3]

        builtin_observation = self.get_builtin_observation(image)
        builtin_action = self.get_builtin_action(_handle)

        res = RoomToGameData(builtin_obs=builtin_observation, builtin_act=builtin_action,
                             custom_obs=custom_data.custom_obs,
                             custom_act=custom_data.custom_act)
        return res

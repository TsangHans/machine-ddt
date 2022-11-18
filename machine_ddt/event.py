from dataclasses import dataclass
from typing import Dict, Callable, Iterable, Sized

import os
import mini_six.portable.win32.operation as operation
import mini_six.portable.win32.windll

from mini_six import Config, Image
from machine_ddt import _scheduler, _scheduler_task_list
from machine_ddt.key_map import KEY_MAP
import numpy as np
import cv2 as cv

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

__all__ = ["InGame", "InRoom", "DDTData"]

config = Config()


@dataclass
class DDTData:
    observation: Dict[str, str]
    action: Dict[str, Callable]


class _DDTEvent:
    def __init__(self, config_fp):
        self.analyze_config = {}
        self.observation_config = {}
        self.action_config = {}
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

    def analyze(self, data: Image):
        """根据截图分析得出属于该状态的概率"""
        image, _handle = data.data, data.handle

        if image.shape[2] == 4:
            image = image[:, :, :3]

        left, up, right, down = self.analyze_config["position"]
        cut_image = image[up:down, left:right, :]

        analyze_method = self.analyze_config["method"]
        if analyze_method == "static_compare":
            compare_image_fp = self.analyze_config["method_param"]["compare_image_fp"]
            compare_image = cv.imread(os.path.join(config.get("static"), compare_image_fp))
            similarity = self.static_compare(cut_image, compare_image)
        else:
            raise ValueError(f"Unexpected value analyze_method={analyze_method}.")

        return similarity

    def get_builtin_observation(self, image: np.ndarray) -> dict:
        raise NotImplementedError("Please reload this method.")

    def get_builtin_action(self, _handle: int) -> dict:
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
                import dl_script

                method_param = observation_config["method_param"]
                preprocess = method_param["preprocess"]
                postprocess = method_param["postprocess"]
                onnx_model_fp = os.path.join(config.get("static"), method_param["onnx_model"])
                character_dict_fp = os.path.join(config.get("static"), method_param["character_dict"])
                input_image_shape = (3, down - up, right - left)

                session = dl_script.load_onnx(onnx_model_fp)
                preprocess_func = dl_script.build_preprocess(algorithm=preprocess)
                postprocess_func = dl_script.build_postprocess(character_dict_fp, algorithm=postprocess)

                norm_image = preprocess_func(cut_image, input_image_shape)
                input_name = session.get_inputs()[0].name
                output = session.run([], {input_name: norm_image})
                obs[observation] = postprocess_func(output)[0][0]

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

        obs, act = {}, {}

        builtin_obs = self.get_builtin_observation(image)
        obs.update(builtin_obs)

        custom_obs = self.get_custom_observation(image)
        obs.update(custom_obs)

        builtin_act = self.get_builtin_action(_handle)
        act.update(builtin_act)

        custom_act = self.get_custom_action(_handle)
        act.update(custom_act)

        data = DDTData(observation=obs, action=act)

        return data


class InEntry:
    """在入口"""
    pass


class InRoom(_DDTEvent):
    """在房间"""

    def get_builtin_observation(self, image: np.ndarray) -> dict:
        raise {}

    def get_builtin_action(self, _handle: int) -> dict:
        raise {}


class InGame(_DDTEvent):
    """在游戏"""

    def get_builtin_observation(self, image: np.ndarray) -> dict:
        raise {}

    def get_builtin_action(self, _handle: int) -> dict:
        raise {}


class RoomToGame(_DDTEvent):
    """由房间进入游戏"""

    def get_builtin_observation(self, image: np.ndarray) -> dict:
        raise {}

    def get_builtin_action(self, _handle: int) -> dict:
        raise {}

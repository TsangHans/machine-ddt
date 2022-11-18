from dataclasses import dataclass
from typing import Dict, Callable

import os
import mini_six.portable.win32.operation as operation

from mini_six import Config, Image
from machine_ddt import _scheduler, _scheduler_task_list
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

    def pull(self, data: Image):
        """拉取该状态下所有信息"""
        image, _handle = data.data, data.handle

        if image.shape[2] == 4:
            image = image[:, :, :3]

        obs = {}

        for observation, observation_config in self.observation_config.items():

            left, up, right, down = observation_config["position"]
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

            elif analyze_method == "onnx":
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

        act = {}
        for action, action_config in self.action_config.items():
            act[action] = {}
            method = action_config["method"]
            if method == "left_click":
                def func():
                    return operation.left_click(_handle, *action_config["param"])

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

        data = DDTData(observation=obs, action=act)

        return data


class InEntry:
    """在入口"""
    pass


class InRoom(_DDTEvent):
    """在房间"""
    pass


class InGame(_DDTEvent):
    """在游戏"""
    pass


class RoomToGame(_DDTEvent):
    """由房间进入游戏"""
    pass




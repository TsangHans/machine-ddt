from dataclasses import dataclass, field
import machine_ddt
from .abstract import BuiltinObservation
import numpy as np
import os
import cv2 as cv

__module_path__ = machine_ddt.__file__.replace("\\__init__.py", "")

from machine_ddt.observe_method import onnx_recognize, static_compare


@dataclass
class InGameObservation(BuiltinObservation):
    wind: float = field(init=False)
    angle: int = field(init=False)
    my_turn: bool = field(init=False)
    host: bool = field(init=False)

    # players: Dict[str, Player](init=False)

    def __post_init__(self):
        self.wind = get_wind(self._image)
        self.angle = get_angle(self._image)
        self.my_turn = get_my_turn_status(self._image)
        self.host = get_host_status(self._image)


def get_wind(image: np.ndarray):
    wind_rec_model_fp = os.path.join(__module_path__,
                                     "static/model/wind_1_rec_en_number_lite/wind_1_rec_en_number_lite.onnx")
    wind_character_dict_fp = os.path.join(__module_path__, "static/model/wind_1_rec_en_number_lite/wind_dict.txt")

    cut_image = image[17:48, 461:537, :]
    h, w, c = cut_image.shape
    input_image_shape = (c, h, w)

    res = onnx_recognize(cut_image, wind_rec_model_fp, wind_character_dict_fp, input_image_shape)
    res = float(res)
    if image[31, 466, 0] == 245:
        res = - res

    return res


def get_angle(image: np.ndarray):
    angle_rec_model_fp = os.path.join(__module_path__,
                                      "static/model/angle_1_rec_en_number_lite/angle_1_rec_en_number_lite.onnx")
    angle_character_dict_fp = os.path.join(__module_path__, "static/model/angle_1_rec_en_number_lite/angle_dict.txt")

    cut_image = image[555:576, 29:73, :]
    h, w, c = cut_image.shape
    input_image_shape = (c, h, w)

    res = onnx_recognize(cut_image, angle_rec_model_fp, angle_character_dict_fp, input_image_shape)
    res = int(res)
    return res


def get_my_turn_status(image: np.ndarray):
    left, up, right, down = 477, 158, 523, 174
    cut_image = image[up:down, left:right]
    in_game_my_turn_img = cv.imread(os.path.join(__module_path__, "static/image/in_game_my_turn.png"))

    my_turn_similarity = static_compare(cut_image, in_game_my_turn_img)

    if my_turn_similarity >= 0.6:
        res = True
    else:
        res = False

    return res


def get_host_status(image: np.ndarray):
    left, up, right, down = 47, 439, 83, 455
    cut_image = image[up:down, left:right]
    in_game_hosting_img = cv.imread(os.path.join(__module_path__, "static/image/in_game_hosting.png"))
    in_game_not_hosting_img = cv.imread(os.path.join(__module_path__, "static/image/in_game_not_hosting.png"))

    in_game_hosting_similarity = static_compare(cut_image, in_game_hosting_img)
    in_game_not_hosting_similarity = static_compare(cut_image, in_game_not_hosting_img)

    if in_game_hosting_similarity >= in_game_not_hosting_similarity:
        res = True
    else:
        res = False

    return res

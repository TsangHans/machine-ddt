from .abstract import BuiltinObservation
from dataclasses import dataclass, field

import machine_ddt
import os
import numpy as np
import cv2 as cv

__module_path__ = machine_ddt.__file__.replace("\\__init__.py", "")

from machine_ddt.observe_method import onnx_recognize, static_compare


@dataclass
class InRoomObservation(BuiltinObservation):
    ready: bool = field(init=False)

    def __post_init__(self):
        self.ready = get_ready_status(self._image)


def get_ready_status(image: np.ndarray):
    cut_image = image[514:529, 929:983]
    in_room_ready_img = cv.imread(os.path.join(__module_path__, "static/image/in_room_ready.png"))
    in_room_start_img = cv.imread(os.path.join(__module_path__, "static/image/in_room_start.png"))

    ready_similarity = static_compare(cut_image, in_room_ready_img)
    start_similarity = static_compare(cut_image, in_room_start_img)

    if ready_similarity >= start_similarity:
        res = True
    else:
        res = False

    return res

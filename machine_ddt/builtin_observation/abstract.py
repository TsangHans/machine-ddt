from dataclasses import dataclass
import numpy as np


@dataclass
class BuiltinObservation:
    _image: np.ndarray

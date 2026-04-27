
import numpy as np

from typing import NamedTuple
from src.method import Method

class InitData(NamedTuple):
    cities: np.ndarray
    method: Method
    gpu: bool
    benchmark: bool
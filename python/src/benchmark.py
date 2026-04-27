
import numpy as np

from dataclasses import dataclass

@dataclass
class Benchmark:
    time_ms: np.uint32
    indices: np.ndarray
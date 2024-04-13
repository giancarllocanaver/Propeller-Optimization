import numpy as np
import pandas as pd

from typing import NamedTuple, List


class Particle(NamedTuple):
    objective_function: float
    variables: np.ndarray
    velocity: np.ndarray
    points_p: np.ndarray
    points_a: np.ndarray
    splines: List[np.ndarray]
    results: pd.DataFrame

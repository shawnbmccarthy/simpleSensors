import random
from typing import Union


def jitter(value: Union[int, float], jitter_amt: float) -> float:
    return value + ((random.random() * 2 - 1) * jitter_amt)


def generate_random(a: float, b: float, r: int = 2) -> float:
    return round(random.uniform(a, b), r)
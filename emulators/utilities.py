import random
from typing import Union


def bounded_jitter(
        value: Union[int, float],
        lower: Union[int, float],
        upper: Union[int, float], jitter_amt: float
) -> float:
    """
    can do better, will work it out later
    """
    val = jitter(value, jitter_amt)
    if val < lower:
        return lower
    if val > upper:
        return upper
    return val


def reset_value(current_value: float, orig: float, delta: float) -> float:
    if abs(current_value - orig) > delta:
        return orig
    return current_value

def bounded_jitter_down(
    value: Union[int, float],
    lower: Union[int, float],
    upper: Union[int, float], jitter_amt: float
) -> float:
    """
    can do better, will work it out later
    """
    val = jitter_down(value, jitter_amt)
    if val < lower:
        return lower
    if val > upper:
        return upper
    return val


def jitter(value: Union[int, float], jitter_amt: float) -> float:
    return value + ((random.random() * 2 - 1) * jitter_amt)


def jitter_down(value: Union[int, float], jitter_amt: float) -> float:
    return value - ((random.random() * 2 - 1) * jitter_amt)


def generate_random(a: float, b: float, r: int = 2) -> float:
    return round(random.uniform(a, b), r)

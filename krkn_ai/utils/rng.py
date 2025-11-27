import numpy as np
from typing import List, Any
from typing import TypeVar, Sequence

T = TypeVar('T')

class RNG:
    def __init__(self):
        self.rng = np.random.default_rng()

    def random(self):
        return self.rng.random()

    def choice(self, items: Sequence[T]) -> T:
        """Return a random element from the given non-empty sequence. The return type is inferred from the list type."""
        return self.rng.choice(items)

    def choices(self, items: List[Any], weights: List[float], k: int = 1):
        return list(self.rng.choice(items, p=weights, size=k))

    def randint(self, low: int, high: int):
        if low == high:
            return low
        return self.rng.integers(low, high)
    
    def uniform(self, low: float, high: float):
        return self.rng.uniform(low, high)

rng = RNG()

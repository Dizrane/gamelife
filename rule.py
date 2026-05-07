from abc import ABC, abstractmethod
from typing import Set

_DIGITS = set("012345678")


def _parse_digits(spec: str) -> Set[int]:
    if spec == "":
        return set()
    if any(c not in _DIGITS for c in spec):
        raise ValueError(f"Rule contains non-digit characters: {spec!r}")
    digits = [int(c) for c in spec]
    if len(set(digits)) != len(digits):
        raise ValueError(f"Rule has duplicate digits: {spec!r}")
    return set(digits)


class Rule(ABC):
    """Абстрактное правило клеточного автомата."""

    @abstractmethod
    def next_state(self, alive: bool, neighbors: int) -> bool:
        """Возвращает следующее состояние клетки."""

    @property
    @abstractmethod
    def b_string(self) -> str:
        """Цифры B (рождение) в каноническом виде."""

    @property
    @abstractmethod
    def s_string(self) -> str:
        """Цифры S (выживание) в каноническом виде."""

    def to_string(self) -> str:
        return f"B{self.b_string}/S{self.s_string}"


class CustomRule(Rule):
    """Параметризуемое правило вида B.../S..."""

    def __init__(self, born: str, survive: str):
        self._born = _parse_digits(born)
        self._survive = _parse_digits(survive)

    def next_state(self, alive: bool, neighbors: int) -> bool:
        if alive:
            return neighbors in self._survive
        return neighbors in self._born

    @property
    def b_string(self) -> str:
        return "".join(str(d) for d in sorted(self._born))

    @property
    def s_string(self) -> str:
        return "".join(str(d) for d in sorted(self._survive))


class ConwayRule(CustomRule):
    """Классическое правило Конвея B3/S23."""

    def __init__(self):
        super().__init__("3", "23")

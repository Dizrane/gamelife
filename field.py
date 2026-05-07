import random
from typing import Iterable, Iterator, Tuple

from point import Point


class Field:
    """Тороидальное поле клеток заданного размера.

    Хранит состояние клеток и инкапсулирует доступ к ним.
    Внешний код не должен знать про внутреннюю структуру `_cells`.
    """

    DEFAULT_SIZE = 20

    def __init__(self, size: int = DEFAULT_SIZE):
        if size <= 0:
            raise ValueError("Field size must be positive")
        self._size = size
        self._cells = [[False] * size for _ in range(size)]

    @property
    def size(self) -> int:
        return self._size

    def _wrap(self, coord: int) -> int:
        return coord % self._size

    def get_state(self, row: int, col: int) -> bool:
        return self._cells[self._wrap(row)][self._wrap(col)]

    def set_state(self, row: int, col: int, value: bool) -> None:
        self._cells[self._wrap(row)][self._wrap(col)] = bool(value)

    def toggle(self, row: int, col: int) -> None:
        r, c = self._wrap(row), self._wrap(col)
        self._cells[r][c] = not self._cells[r][c]

    def clear(self) -> None:
        for row in self._cells:
            for i in range(self._size):
                row[i] = False

    def randomize(self, density: float = 0.5) -> None:
        for r in range(self._size):
            for c in range(self._size):
                self._cells[r][c] = random.random() < density

    def alive_count(self) -> int:
        return sum(1 for row in self._cells for v in row if v)

    def alive_cells(self) -> Iterator[Tuple[int, int]]:
        for r in range(self._size):
            for c in range(self._size):
                if self._cells[r][c]:
                    yield r, c

    def populate(self, points: Iterable[Point]) -> None:
        for p in points:
            self.set_state(p.x, p.y, True)

    def count_neighbors(self, row: int, col: int) -> int:
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                if self.get_state(row + dr, col + dc):
                    count += 1
        return count

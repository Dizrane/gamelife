from typing import Iterable, Optional

from field import Field
from point import Point
from rule import ConwayRule, Rule


class GameModel:
    """Модель игры «Жизнь».

    Объединяет поле и правило, скрывает их от внешнего мира
    за фасадом методов и свойств.
    """

    DEFAULT_NAME = "Conway's Game of Life"

    def __init__(
        self,
        name: str = DEFAULT_NAME,
        rule: Optional[Rule] = None,
        points: Optional[Iterable[Point]] = None,
        size: int = Field.DEFAULT_SIZE,
    ):
        self._name = name
        self._rule = rule if rule is not None else ConwayRule()
        self._iteration = 0
        self._field = Field(size)
        self._buffer = Field(size)
        if points:
            self._field.populate(points)

    @property
    def name(self) -> str:
        return self._name

    @property
    def iteration(self) -> int:
        return self._iteration

    @property
    def rule(self) -> Rule:
        return self._rule

    @property
    def size(self) -> int:
        return self._field.size

    def cell_state(self, row: int, col: int) -> bool:
        return self._field.get_state(row, col)

    def alive_cells(self):
        return self._field.alive_cells()

    def alive_count(self) -> int:
        return self._field.alive_count()

    def toggle_cell(self, row: int, col: int) -> None:
        self._field.toggle(row, col)

    def clear(self) -> None:
        self._field.clear()
        self._iteration = 0

    def randomize(self) -> None:
        self._field.randomize()
        self._iteration = 0

    def compute_iteration(self) -> None:
        size = self._field.size
        for r in range(size):
            for c in range(size):
                alive = self._field.get_state(r, c)
                neighbors = self._field.count_neighbors(r, c)
                self._buffer.set_state(r, c, self._rule.next_state(alive, neighbors))
        self._field, self._buffer = self._buffer, self._field
        self._iteration += 1

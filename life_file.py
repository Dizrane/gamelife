from typing import List, Tuple

from game_model import GameModel
from point import Point
from rule import CustomRule, Rule


class LifeFileIO:
    """Сохранение и загрузка состояния игры в формате Life 1.06."""

    HEADER = "#Life 1.06"
    DEFAULT_LOADED_NAME = "Loaded universe"
    DEFAULT_B_RULE = "3"
    DEFAULT_S_RULE = "23"

    @classmethod
    def save(cls, model: GameModel, filename: str) -> None:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(cls.HEADER + "\n")
            f.write(f"#N {model.name}\n")
            f.write(f"#R {model.rule.to_string()}\n")
            for row, col in model.alive_cells():
                f.write(f"{row} {col}\n")

    @classmethod
    def load(cls, filename: str) -> GameModel:
        name = cls.DEFAULT_LOADED_NAME
        b_rule = cls.DEFAULT_B_RULE
        s_rule = cls.DEFAULT_S_RULE
        points: List[Point] = []

        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    parsed = cls._parse_header(line)
                    if parsed is not None:
                        key, value = parsed
                        if key == "name":
                            name = value
                        elif key == "rule":
                            b_rule, s_rule = cls._parse_rule_spec(value)
                    continue
                parts = line.split()
                if len(parts) == 2:
                    points.append(Point(int(parts[0]), int(parts[1])))

        rule: Rule = CustomRule(b_rule, s_rule)
        return GameModel(name=name, rule=rule, points=points)

    @staticmethod
    def _parse_header(line: str):
        if line.startswith("#N "):
            return "name", line[3:].strip()
        if line.startswith("#R "):
            return "rule", line[3:].strip()
        return None

    @staticmethod
    def _parse_rule_spec(spec: str) -> Tuple[str, str]:
        if spec.startswith("B") and "/S" in spec:
            b_part, s_part = spec[1:].split("/S", 1)
            return b_part, s_part
        return LifeFileIO.DEFAULT_B_RULE, LifeFileIO.DEFAULT_S_RULE

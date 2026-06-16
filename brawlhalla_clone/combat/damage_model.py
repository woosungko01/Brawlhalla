# combat/damage_model.py

from dataclasses import dataclass


@dataclass
class DamageState:
    percent: float = 0.0

    def add_damage(self, amount: float) -> None:
        self.percent += amount

    def reset(self) -> None:
        self.percent = 0.0
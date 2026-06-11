#combat/damage_model.py

from dataclasses import dataclass


@dataclass
class DamageState:
    percent: float = 0.0

    def add_damage(self, amount: float) -> None:
        self.percent += amount
# combat/damage_model.py

from dataclasses import dataclass


@dataclass
class DamageState:
    #입은 데미지 처리
    percent: float = 0.0

    def add_damage(self, amount: float) -> None:
        self.percent += amount

    def reset(self) -> None:
        self.percent = 0.0
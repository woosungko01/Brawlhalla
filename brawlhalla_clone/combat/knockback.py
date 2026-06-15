# combat/knockback.py

from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class HitEffect:
    damage: float
    vx: float
    vy: float
    hitstun: float
    stun: float = 0.0
    delayed_launch: bool = False


class KnockbackModel(ABC):
    @abstractmethod
    def build_effect(self, attacker, target) -> HitEffect:
        raise NotImplementedError


class FixedKnockback(KnockbackModel):
    def __init__(
        self,
        damage: float,
        vx: float,
        vy: float,
        hitstun: float,
        stun: float = 0.0,
        delayed_launch: bool = False,
    ) -> None:
        self.damage = damage
        self.vx = vx
        self.vy = vy
        self.hitstun = hitstun
        self.stun = stun
        self.delayed_launch = delayed_launch

    def build_effect(self, attacker, target) -> HitEffect:
        return HitEffect(
            damage=self.damage,
            vx=attacker.facing * self.vx,
            vy=self.vy,
            hitstun=self.hitstun,
            stun=self.stun,
            delayed_launch=self.delayed_launch,
        )
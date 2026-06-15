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


class ScalingKnockback(KnockbackModel):
    def __init__(
        self,
        damage: float,
        base_vx: float,
        base_vy: float,
        hitstun: float,
        percent_scale: float,
        stun: float = 0.0,
        delayed_launch: bool = False,
    ) -> None:
        self.damage = damage
        self.base_vx = base_vx
        self.base_vy = base_vy
        self.hitstun = hitstun
        self.percent_scale = percent_scale
        self.stun = stun
        self.delayed_launch = delayed_launch

    def build_effect(self, attacker, target) -> HitEffect:
        scale = 1.0 + target.damage.percent * self.percent_scale
        return HitEffect(
            damage=self.damage,
            vx=attacker.facing * self.base_vx * scale,
            vy=self.base_vy * scale,
            hitstun=self.hitstun,
            stun=self.stun,
            delayed_launch=self.delayed_launch,
        )
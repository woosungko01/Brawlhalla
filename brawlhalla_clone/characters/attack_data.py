from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

import pygame


@dataclass
class HitEffect:
    vx: float
    vy: float
    hitstun: float


@dataclass
class AttackData:
    name: str
    total_time: float
    active_start: float
    active_end: float
    hitbox_factory: Callable[[object], pygame.Rect | None]
    hit_effect_factory: Callable[[object, object], HitEffect]
    locks_horizontal_movement: bool = True
    dash_velocity_x: float = 0.0
    repeated_hit_interval: float | None = None
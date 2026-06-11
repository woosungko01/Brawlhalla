from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

import pygame
from combat.knockback import KnockbackModel


@dataclass
class AttackData:
    name: str
    total_time: float
    active_start: float
    active_end: float
    hitbox_factory: Callable[[object], pygame.Rect | None]
    knockback_model: KnockbackModel
    locks_horizontal_movement: bool = True
    dash_velocity_x: float = 0.0
    repeated_hit_interval: float | None = None
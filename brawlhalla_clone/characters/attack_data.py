from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

import pygame
from combat.knockback import KnockbackModel


@dataclass
class AttackData:
    #공격/스킬 처리 시 필요한 정보 기본 설정
    name: str
    total_time: float
    active_windows: list[tuple[float, float]]
    hitbox_factory: Callable[[object], pygame.Rect | None]
    knockback_model: KnockbackModel
    locks_horizontal_movement: bool = True
    dash_velocity_x: float = 0.0
    dash_start_time: float = 0.0
    repeated_hit_interval: float | None = None
    allow_multi_hit: bool = False
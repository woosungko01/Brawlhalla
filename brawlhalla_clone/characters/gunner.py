# characters/gunner.py

from __future__ import annotations
import pygame

from characters.base_character import BaseCharacter
from characters.attack_data import AttackData
from characters.attack_slots import AttackSlot
from combat.knockback import FixedKnockback, ScalingKnockback


def _facing_rect(center_x: float, top_y: float, width: float, height: float, facing: int) -> pygame.Rect:
    if facing >= 0:
        x = center_x
    else:
        x = center_x - width
    return pygame.Rect(int(x), int(top_y), int(width), int(height))


class GunnerCharacter(BaseCharacter):
    character_id = "gunner"

    def get_attack_for_slot(self, slot: AttackSlot) -> AttackData | None:
        if slot == AttackSlot.NEUTRAL:
            return self._neutral()
        if slot == AttackSlot.SIDE:
            return self._side()
        if slot == AttackSlot.UP:
            return self._up()
        if slot == AttackSlot.UP_AIR:
            return self._up_air()
        if slot == AttackSlot.DOWN_GROUND:
            return self._down_ground()
        if slot == AttackSlot.DOWN_AIR:
            return self._down_air()
        return None

    def try_start_ultimate(self, fighter) -> bool:
        atk = self._ultimate()
        fighter.start_attack(atk)
        fighter.attack_tick_timer = 0.0
        return True

    def _neutral(self) -> AttackData:
        return AttackData(
            name=AttackSlot.NEUTRAL.value,
            total_time=0.22,
            active_windows=[(0.00, 0.10)],
            hitbox_factory=lambda f: _facing_rect(
                f.pos.x + f.facing * 18,
                f.pos.y + 16,
                88,
                28,
                f.facing,
            ),
            knockback_model=ScalingKnockback(
                damage=6.0,
                base_vx=120.0,
                base_vy=40.0,
                hitstun=0.10,
                percent_scale=0.010,
            ),
        )

    def _side(self) -> AttackData:
        return AttackData(
            name=AttackSlot.SIDE.value,
            total_time=0.48,
            active_windows=[
                (0.20, 0.24),
                (0.32, 0.36),
                (0.44, 0.48),
            ],
            hitbox_factory=lambda f: _facing_rect(
                f.pos.x + f.facing * 18,
                f.pos.y - 12,
                140,
                18,
                f.facing,
            ),
            knockback_model=FixedKnockback(
                damage=14.0,
                vx=70.0,
                vy=-60.0,
                hitstun=0.28,
                stun=0.38,
                delayed_launch=True,
            ),
            allow_multi_hit=True,
        )

    def _up(self) -> AttackData:
        return AttackData(
            name=AttackSlot.UP.value,
            total_time=0.24,
            active_windows=[(0.00, 0.10)],
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x - 62),
                int(f.pos.y - 112),
                124,
                62,
            ),
            knockback_model=ScalingKnockback(
                damage=8.0,
                base_vx=0.0,
                base_vy=-520.0,
                hitstun=0.14,
                percent_scale=0.012,
            ),
        )

    def _up_air(self) -> AttackData:
        return AttackData(
            name=AttackSlot.UP_AIR.value,
            total_time=0.46,
            active_windows=[
                (0.16, 0.20),
                (0.26, 0.30),
                (0.36, 0.40),
            ],
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x - 62),
                int(f.pos.y - 120),
                124,
                78,
            ),
            knockback_model=FixedKnockback(
                damage=13.0,
                vx=0.0,
                vy=-80.0,
                hitstun=0.26,
                stun=0.36,
                delayed_launch=True,
            ),
            allow_multi_hit=True,
        )

    def _down_ground(self) -> AttackData:
        return AttackData(
            name=AttackSlot.DOWN_GROUND.value,
            total_time=0.24,
            active_windows=[(0.00, 0.10)],
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x - 62),
                int(f.pos.y + 20),
                124,
                62,
            ),
            knockback_model=ScalingKnockback(
                damage=8.0,
                base_vx=0.0,
                base_vy=540.0,
                hitstun=0.14,
                percent_scale=0.012,
            ),
        )

    def _down_air(self) -> AttackData:
        return AttackData(
            name=AttackSlot.DOWN_AIR.value,
            total_time=0.24,
            active_windows=[(0.00, 0.10)],
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x - 62),
                int(f.pos.y + 28),
                124,
                74,
            ),
            knockback_model=ScalingKnockback(
                damage=9.0,
                base_vx=0.0,
                base_vy=620.0,
                hitstun=0.16,
                percent_scale=0.014,
            ),
        )

    def _ultimate(self) -> AttackData:
        return AttackData(
            name=AttackSlot.ULTIMATE.value,
            total_time=4.0,
            active_windows=[(0.0, 4.0)],
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x - 160),
                int(f.pos.y - 160),
                320,
                320,
            ),
            knockback_model=FixedKnockback(3.0, 180.0, -120.0, 0.08),
            locks_horizontal_movement=False,
            repeated_hit_interval=0.12,
        )
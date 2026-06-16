# characters/brawler.py

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


class BrawlerCharacter(BaseCharacter):
    character_id = "brawler"

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
        fighter.ultimate_timer = 5.0
        return True

    def _neutral(self) -> AttackData:
        return AttackData(
            name=AttackSlot.NEUTRAL.value,
            total_time=0.34,
            active_windows=[(0.00, 0.12)],
            hitbox_factory=lambda f: _facing_rect(
                f.pos.x + f.facing * 34,
                f.pos.y - 30,
                72,
                84,
                f.facing,
            ),
            knockback_model=ScalingKnockback(
                damage=11.0,
                base_vx=200.0,
                base_vy=-380.0,
                hitstun=0.22,
                percent_scale=0.012,
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
                f.pos.x + f.facing * 44,
                f.pos.y - 10,
                74,
                40,
                f.facing,
            ),
            knockback_model=FixedKnockback(
                damage=14.0,
                vx=90.0,
                vy=-70.0,
                hitstun=0.30,
                stun=0.40,
                delayed_launch=True,
            ),
            allow_multi_hit=True,
        )

    def _up(self) -> AttackData:
        return AttackData(
            name=AttackSlot.UP.value,
            total_time=0.34,
            active_windows=[(0.00, 0.12)],
            hitbox_factory=lambda f: _facing_rect(
                f.pos.x + f.facing * 26,
                f.pos.y - 86,
                92,
                76,
                f.facing,
            ),
            knockback_model=ScalingKnockback(
                damage=10.0,
                base_vx=120.0,
                base_vy=-520.0,
                hitstun=0.22,
                percent_scale=0.013,
            ),
        )

    def _up_air(self) -> AttackData:
        return AttackData(
            name=AttackSlot.UP_AIR.value,
            total_time=0.48,
            active_windows=[
                (0.18, 0.22),
                (0.28, 0.32),
                (0.38, 0.42),
            ],
            hitbox_factory=lambda f: _facing_rect(
                f.pos.x + f.facing * 26,
                f.pos.y - 98,
                96,
                84,
                f.facing,
            ),
            knockback_model=FixedKnockback(
                damage=13.0,
                vx=70.0,
                vy=-90.0,
                hitstun=0.28,
                stun=0.38,
                delayed_launch=True,
            ),
            locks_horizontal_movement=False,
            dash_velocity_x=180.0,
            allow_multi_hit=True,
        )

    def _down_ground(self) -> AttackData:
        return AttackData(
            name=AttackSlot.DOWN_GROUND.value,
            total_time=0.38,
            active_windows=[(0.00, 0.12)],
            hitbox_factory=lambda f: _facing_rect(
                f.pos.x + f.facing * 32,
                f.pos.y + 6,
                92,
                52,
                f.facing,
            ),
            knockback_model=ScalingKnockback(
                damage=10.0,
                base_vx=220.0,
                base_vy=-160.0,
                hitstun=0.20,
                percent_scale=0.014,
            ),
            locks_horizontal_movement=False,
            dash_velocity_x=260.0,
        )

    def _down_air(self) -> AttackData:
        return AttackData(
            name=AttackSlot.DOWN_AIR.value,
            total_time=0.46,
            active_windows=[
                (0.16, 0.20),
                (0.26, 0.30),
                (0.36, 0.40),
            ],
            hitbox_factory=lambda f: _facing_rect(
                f.pos.x + f.facing * 28,
                f.pos.y + 12,
                88,
                54,
                f.facing,
            ),
            knockback_model=FixedKnockback(
                damage=13.0,
                vx=80.0,
                vy=90.0,
                hitstun=0.26,
                stun=0.36,
                delayed_launch=True,
            ),
            locks_horizontal_movement=False,
            dash_velocity_x=240.0,
            allow_multi_hit=True,
        )
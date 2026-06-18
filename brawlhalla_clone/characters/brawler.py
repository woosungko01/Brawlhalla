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
            total_time=0.49,
            active_windows=[(0.15, 0.27)],
            hitbox_factory=lambda f: _facing_rect(
                f.pos.x + f.facing * 34,
                f.pos.y - 30,
                72,
                84,
                f.facing,
            ),
            knockback_model=ScalingKnockback(
                damage=11.0,
                base_vx=250.0,
                base_vy=-460.0,
                hitstun=0.24,
                percent_scale=0.030,
            ),
        )

    def _side(self) -> AttackData:
        return AttackData(
            name=AttackSlot.SIDE.value,
            total_time=0.72,
            active_windows=[
                (0.33, 0.39),
                (0.44, 0.50),
                (0.55, 0.61),
            ],
            hitbox_factory=lambda f: _facing_rect(
                f.pos.x + f.facing * 12,
                f.pos.y - 12,
                72,
                42,
                f.facing,
            ),
            knockback_model=FixedKnockback(
                damage=14.0,
                vx=180.0,
                vy=-105.0,
                hitstun=0.38,
                stun=0.58,
                delayed_launch=True,
            ),
            locks_horizontal_movement=False,
            dash_velocity_x=880.0,
            dash_start_time=0.29,
            allow_multi_hit=True,
        )

    def _up(self) -> AttackData:
        return AttackData(
            name=AttackSlot.UP.value,
            total_time=0.49,
            active_windows=[(0.15, 0.27)],
            hitbox_factory=lambda f: _facing_rect(
                f.pos.x + f.facing * 26,
                f.pos.y - 86,
                92,
                76,
                f.facing,
            ),
            knockback_model=ScalingKnockback(
                damage=10.0,
                base_vx=150.0,
                base_vy=-640.0,
                hitstun=0.24,
                percent_scale=0.032,
            ),
        )

    def _up_air(self) -> AttackData:
        return AttackData(
            name=AttackSlot.UP_AIR.value,
            total_time=0.63,
            active_windows=[
                (0.33, 0.38),
                (0.43, 0.48),
                (0.53, 0.58),
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
                vx=130.0,
                vy=-145.0,
                hitstun=0.36,
                stun=0.54,
                delayed_launch=True,
            ),
            locks_horizontal_movement=False,
            dash_velocity_x=180.0,
            dash_start_time=0.30,
            allow_multi_hit=True,
        )

    def _down_ground(self) -> AttackData:
        return AttackData(
            name=AttackSlot.DOWN_GROUND.value,
            total_time=0.53,
            active_windows=[(0.15, 0.27)],
            hitbox_factory=lambda f: _facing_rect(
                f.pos.x + f.facing * 32,
                f.pos.y + 6,
                92,
                52,
                f.facing,
            ),
            knockback_model=ScalingKnockback(
                damage=10.0,
                base_vx=280.0,
                base_vy=-220.0,
                hitstun=0.22,
                percent_scale=0.032,
            ),
            locks_horizontal_movement=False,
            dash_velocity_x=260.0,
            dash_start_time=0.14,
        )

    def _down_air(self) -> AttackData:
        return AttackData(
            name=AttackSlot.DOWN_AIR.value,
            total_time=0.61,
            active_windows=[
                (0.31, 0.36),
                (0.41, 0.46),
                (0.51, 0.56),
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
                vx=130.0,
                vy=145.0,
                hitstun=0.34,
                stun=0.52,
                delayed_launch=True,
            ),
            locks_horizontal_movement=False,
            dash_velocity_x=240.0,
            dash_start_time=0.28,
            allow_multi_hit=True,
        )
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


class SwordsmanCharacter(BaseCharacter):
    #swordsman에 대한 설정
    character_id = "swordsman"

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
        fighter.start_attack(self._ultimate())
        return True

    def _neutral(self) -> AttackData:
        return AttackData(
            name=AttackSlot.NEUTRAL.value,
            total_time=0.59,
            active_windows=[
                (0.31, 0.35),
                (0.41, 0.45),
                (0.51, 0.55),
            ],
            hitbox_factory=lambda f: _facing_rect(
                f.pos.x + f.facing * 24,
                f.pos.y - 36,
                56,
                76,
                f.facing,
            ),
            knockback_model=FixedKnockback(
                damage=13.0,
                vx=110.0,
                vy=-110.0,
                hitstun=0.36,
                stun=0.56,
                delayed_launch=True,
            ),
            allow_multi_hit=True,
        )

    def _side(self) -> AttackData:
        return AttackData(
            name=AttackSlot.SIDE.value,
            total_time=0.66,
            active_windows=[
                (0.30, 0.34),
                (0.40, 0.44),
                (0.50, 0.54),
            ],
            hitbox_factory=lambda f: _facing_rect(
                f.pos.x + f.facing * 12,
                f.pos.y - 16,
                64,
                42,
                f.facing,
            ),
            knockback_model=FixedKnockback(
                damage=15.0,
                vx=135.0,
                vy=-115.0,
                hitstun=0.38,
                stun=0.60,
                delayed_launch=True,
            ),
            locks_horizontal_movement=False,
            dash_velocity_x=880.0,
            dash_start_time=0.27,
            allow_multi_hit=True,
        )

    def _up(self) -> AttackData:
        return AttackData(
            name=AttackSlot.UP.value,
            total_time=0.49,
            active_windows=[(0.15, 0.27)],
            hitbox_factory=lambda f: _facing_rect(
                f.pos.x + f.facing * 14,
                f.pos.y - 88,
                110,
                74,
                f.facing,
            ),
            knockback_model=ScalingKnockback(
                damage=11.0,
                base_vx=150.0,
                base_vy=-760.0,
                hitstun=0.26,
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
                f.pos.x + f.facing * 20,
                f.pos.y - 108,
                112,
                92,
                f.facing,
            ),
            knockback_model=FixedKnockback(
                damage=14.0,
                vx=120.0,
                vy=-145.0,
                hitstun=0.37,
                stun=0.58,
                delayed_launch=True,
            ),
            allow_multi_hit=True,
        )

    def _down_ground(self) -> AttackData:
        return AttackData(
            name=AttackSlot.DOWN_GROUND.value,
            total_time=0.51,
            active_windows=[(0.15, 0.27)],
            hitbox_factory=lambda f: _facing_rect(
                f.pos.x + f.facing * 38,
                f.pos.y + 8,
                105,
                70,
                f.facing,
            ),
            knockback_model=ScalingKnockback(
                damage=11.0,
                base_vx=220.0,
                base_vy=520.0,
                hitstun=0.24,
                percent_scale=0.033,
            ),
        )

    def _down_air(self) -> AttackData:
        return AttackData(
            name=AttackSlot.DOWN_AIR.value,
            total_time=0.51,
            active_windows=[(0.15, 0.27)],
            hitbox_factory=lambda f: _facing_rect(
                f.pos.x + f.facing * 22,
                f.pos.y + 16,
                108,
                84,
                f.facing,
            ),
            knockback_model=ScalingKnockback(
                damage=12.0,
                base_vx=170.0,
                base_vy=640.0,
                hitstun=0.26,
                percent_scale=0.033,
            ),
        )

    def _ultimate(self) -> AttackData:
        def hitbox(f):
            elapsed = f.attack_total_time - f.attack_timer
            if not (1.00 <= elapsed <= 1.12):
                return None
            w = 500
            h = 160
            y = f.pos.y - 80
            if f.facing >= 0:
                x = f.pos.x + 10
            else:
                x = f.pos.x - 10 - w
            return pygame.Rect(int(x), int(y), w, h)

        return AttackData(
            name=AttackSlot.ULTIMATE.value,
            total_time=1.20,
            active_windows=[(1.00, 1.12)],
            hitbox_factory=hitbox,
            knockback_model=FixedKnockback(18.0, 520.0, -520.0, 0.40),
        )
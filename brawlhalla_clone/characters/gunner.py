# characters/gunner.py

from __future__ import annotations
import pygame

from characters.base_character import BaseCharacter
from characters.attack_data import AttackData
from characters.attack_slots import AttackSlot
from combat.knockback import FixedKnockback

#stun 구현방식
#stun_timer 시작 + pending_launch 저장
#stun 끝남
#launch 발사 시작
#hitstun_timer 시작
#(중력, 이동속도 받으며 hitstun 적용)


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
            total_time=0.14,
            active_start=0.03,
            active_end=0.08,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x + 18 if f.facing == 1 else f.pos.x - 18 - 80),
                int(f.pos.y + 18),
                80,
                26,
            ),
            knockback_model=FixedKnockback(5.0, 120.0, 60.0, 0.08),
        )

    def _side(self) -> AttackData:
        return AttackData(
            name=AttackSlot.SIDE.value,
            total_time=0.12,
            active_start=0.02,
            active_end=0.06,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x + 18 if f.facing == 1 else f.pos.x - 18 - 140),
                int(f.pos.y - 12),
                140,
                18,
            ),
            knockback_model=FixedKnockback(6.0, 220.0, -40.0, 0.10),
        )

    def _up(self) -> AttackData:
        return AttackData(
            name=AttackSlot.UP.value,
            total_time=0.14,
            active_start=0.03,
            active_end=0.08,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x - 60),
                int(f.pos.y - 110),
                120,
                60,
            ),
            knockback_model=FixedKnockback(7.0, 0.0, -520.0, 0.12),
        )

    def _up_air(self) -> AttackData:
        return AttackData(
            name=AttackSlot.UP_AIR.value,
            total_time=0.14,
            active_start=0.03,
            active_end=0.08,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x - 60),
                int(f.pos.y - 118),
                120,
                72,
            ),
            knockback_model=FixedKnockback(8.0, 0.0, -620.0, 0.14),
        )

    def _down_ground(self) -> AttackData:
        return AttackData(
            name=AttackSlot.DOWN_GROUND.value,
            total_time=0.14,
            active_start=0.03,
            active_end=0.08,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x - 60),
                int(f.pos.y + 20),
                120,
                60,
            ),
            knockback_model=FixedKnockback(7.0, 0.0, 560.0, 0.12),
        )

    def _down_air(self) -> AttackData:
        return AttackData(
            name=AttackSlot.DOWN_AIR.value,
            total_time=0.14,
            active_start=0.03,
            active_end=0.08,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x - 60),
                int(f.pos.y + 28),
                120,
                72,
            ),
            knockback_model=FixedKnockback(8.0, 0.0, 660.0, 0.14),
        )

    def _ultimate(self) -> AttackData:
        return AttackData(
            name=AttackSlot.ULTIMATE.value,
            total_time=4.0,
            active_start=0.0,
            active_end=4.0,
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
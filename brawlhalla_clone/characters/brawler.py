# characters/brawler.py

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
            total_time=0.40,
            active_start=0.10,
            active_end=0.20,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x + f.facing * 30 - 35),
                int(f.pos.y - 75),
                70 + (55 if f.ultimate_timer > 0.0 else 0),
                90,
            ),
            knockback_model=FixedKnockback(12.0, 260.0, -420.0, 0.20),
        )

    def _side(self) -> AttackData:
        return AttackData(
            name=AttackSlot.SIDE.value,
            total_time=0.16,
            active_start=0.03,
            active_end=0.10,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x + f.facing * 35 - ((55 + (55 if f.ultimate_timer > 0.0 else 0)) / 2)),
                int(f.pos.y - 10),
                55 + (55 if f.ultimate_timer > 0.0 else 0),
                36,
            ),
            knockback_model=FixedKnockback(6.0, 170.0, -90.0, 0.10),
        )

    def _up(self) -> AttackData:
        return AttackData(
            name=AttackSlot.UP.value,
            total_time=0.40,
            active_start=0.08,
            active_end=0.32,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x + f.facing * 38 - ((90 + (55 if f.ultimate_timer > 0.0 else 0)) / 2)),
                int(f.pos.y - 24),
                90 + (55 if f.ultimate_timer > 0.0 else 0),
                60,
            ),
            knockback_model=FixedKnockback(10.0, 180.0, -520.0, 0.18),
        )

    def _up_air(self) -> AttackData:
        return AttackData(
            name=AttackSlot.UP_AIR.value,
            total_time=0.40,
            active_start=0.08,
            active_end=0.32,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x + f.facing * 38 - ((90 + (55 if f.ultimate_timer > 0.0 else 0)) / 2)),
                int(f.pos.y - 40),
                90 + (55 if f.ultimate_timer > 0.0 else 0),
                70,
            ),
            knockback_model=FixedKnockback(11.0, 140.0, -620.0, 0.20),
            locks_horizontal_movement=False,
            dash_velocity_x=220.0,
        )

    def _down_ground(self) -> AttackData:
        return AttackData(
            name=AttackSlot.DOWN_GROUND.value,
            total_time=0.40,
            active_start=0.08,
            active_end=0.32,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x + f.facing * 38 - ((90 + (55 if f.ultimate_timer > 0.0 else 0)) / 2)),
                int(f.pos.y - 6),
                90 + (55 if f.ultimate_timer > 0.0 else 0),
                46,
            ),
            knockback_model=FixedKnockback(10.0, 260.0, -220.0, 0.18),
            locks_horizontal_movement=False,
            dash_velocity_x=500.0,
        )

    def _down_air(self) -> AttackData:
        return AttackData(
            name=AttackSlot.DOWN_AIR.value,
            total_time=0.40,
            active_start=0.08,
            active_end=0.32,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x + f.facing * 38 - ((90 + (55 if f.ultimate_timer > 0.0 else 0)) / 2)),
                int(f.pos.y + 10),
                90 + (55 if f.ultimate_timer > 0.0 else 0),
                46,
            ),
            knockback_model=FixedKnockback(11.0, 160.0, 320.0, 0.20),
            locks_horizontal_movement=False,
            dash_velocity_x=300.0,
        )
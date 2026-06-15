# characters/swordsman.py

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


class SwordsmanCharacter(BaseCharacter):
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
            total_time=0.30,
            active_start=0.05,
            active_end=0.20,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x + f.facing * 28 - 21),
                int(f.pos.y - 36),
                42,
                72,
            ),
            knockback_model=FixedKnockback(8.0, 0.0, 0.0, 0.22),
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
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x + f.facing * 58),
                int(f.pos.y - 14),
                90,
                42,
            ),
            knockback_model=FixedKnockback(
                damage=15.0,
                vx=80.0,
                vy=-80.0,
                hitstun=0.30,
                stun=0.40,
                delayed_launch=True,
            ),
            allow_multi_hit=True,
        )

    def _up(self) -> AttackData:
        return AttackData(
            name=AttackSlot.UP.value,
            total_time=0.36,
            active_start=0.14,
            active_end=0.24,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x + f.facing * 38 - ((105 + (55 if f.ultimate_timer > 0.0 else 0)) / 2)),
                int(f.pos.y - 88),
                105 + (55 if f.ultimate_timer > 0.0 else 0),
                70,
            ),
            knockback_model=FixedKnockback(11.0, 110.0, -680.0, 0.24),
        )

    def _up_air(self) -> AttackData:
        return AttackData(
            name=AttackSlot.UP_AIR.value,
            total_time=0.36,
            active_start=0.14,
            active_end=0.24,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x + f.facing * 28 - ((105 + (55 if f.ultimate_timer > 0.0 else 0)) / 2)),
                int(f.pos.y - 108),
                105 + (55 if f.ultimate_timer > 0.0 else 0),
                90,
            ),
            knockback_model=FixedKnockback(
                damage=10.0,
                vx=180.0,
                vy=-760.0,
                hitstun=0.30,
                stun=1,
                delayed_launch=True,
            ),
        )

    def _down_ground(self) -> AttackData:
        return AttackData(
            name=AttackSlot.DOWN_GROUND.value,
            total_time=0.36,
            active_start=0.14,
            active_end=0.24,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x + f.facing * 38),
                int(f.pos.y + 8),
                105,
                70,
            ),
            knockback_model=FixedKnockback(11.0, 160.0, 420.0, 0.22),

        )

    def _down_air(self) -> AttackData:
        return AttackData(
            name=AttackSlot.DOWN_AIR.value,
            total_time=0.36,
            active_start=0.14,
            active_end=0.24,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x + f.facing * 38 - ((105 + (55 if f.ultimate_timer > 0.0 else 0)) / 2)),
                int(f.pos.y + 16),
                105 + (55 if f.ultimate_timer > 0.0 else 0),
                80,
            ),
            knockback_model=FixedKnockback(12.0, 120.0, 520.0, 0.24),
        )

    def _ultimate(self) -> AttackData:
        def hitbox(f):
            elapsed = f.attack_total_time - f.attack_timer
            if not (1.00 <= elapsed <= 1.12):
                return None
            w = 500
            h = 160
            y = f.pos.y - 80
            x = f.pos.x + 10 if f.facing == 1 else f.pos.x - 10 - w
            return pygame.Rect(int(x), int(y), w, h)

        return AttackData(
            name=AttackSlot.ULTIMATE.value,
            total_time=1.20,
            active_start=1.00,
            active_end=1.12,
            hitbox_factory=hitbox,
            knockback_model=FixedKnockback(18.0, 520.0, -520.0, 0.40),
        )
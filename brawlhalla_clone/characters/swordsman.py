# characters/swordsman.py

from __future__ import annotations
import pygame

from characters.base_character import BaseCharacter
from characters.attack_data import AttackData, HitEffect
from characters.attack_slots import AttackSlot


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
            hit_effect_factory=lambda a, t: HitEffect(0.0, 0.0, 0.50),
        )

    def _side(self) -> AttackData:
        return AttackData(
            name=AttackSlot.SIDE.value,
            total_time=0.30,
            active_start=0.12,
            active_end=0.20,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x + f.facing * 58 - ((105 + (55 if f.ultimate_timer > 0.0 else 0)) / 2)),
                int(f.pos.y - 14),
                105 + (55 if f.ultimate_timer > 0.0 else 0),
                42,
            ),
            hit_effect_factory=lambda a, t: HitEffect(a.facing * 340.0, -180.0, 0.18),
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
            hit_effect_factory=lambda a, t: HitEffect(a.facing * 120.0, -900.0, 0.28),
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
            hit_effect_factory=lambda a, t: HitEffect(a.facing * 90.0, -980.0, 0.28),
        )

    def _down_ground(self) -> AttackData:
        return AttackData(
            name=AttackSlot.DOWN_GROUND.value,
            total_time=0.36,
            active_start=0.14,
            active_end=0.24,
            hitbox_factory=lambda f: pygame.Rect(
                int(f.pos.x + f.facing * 38 - ((105 + (55 if f.ultimate_timer > 0.0 else 0)) / 2)),
                int(f.pos.y + 8),
                105 + (55 if f.ultimate_timer > 0.0 else 0),
                70,
            ),
            hit_effect_factory=lambda a, t: HitEffect(a.facing * 150.0, 920.0, 0.28),
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
            hit_effect_factory=lambda a, t: HitEffect(a.facing * 100.0, 980.0, 0.28),
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
            hit_effect_factory=lambda a, t: HitEffect(a.facing * 900.0, -720.0, 0.55),
        )
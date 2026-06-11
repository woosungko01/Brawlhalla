# characters/gunner.py

from __future__ import annotations
import pygame

from characters.base_character import BaseCharacter
from characters.attack_data import AttackData, HitEffect
from characters.attack_slots import AttackSlot


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
            hit_effect_factory=lambda a, t: HitEffect(a.facing * 220.0, 80.0, 0.10),
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
            hit_effect_factory=lambda a, t: HitEffect(a.facing * 420.0, -50.0, 0.12),
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
            hit_effect_factory=lambda a, t: HitEffect(0.0, -820.0, 0.16),
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
            hit_effect_factory=lambda a, t: HitEffect(0.0, -920.0, 0.16),
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
            hit_effect_factory=lambda a, t: HitEffect(0.0, 900.0, 0.16),
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
            hit_effect_factory=lambda a, t: HitEffect(0.0, 980.0, 0.16),
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
            hit_effect_factory=lambda a, t: HitEffect(
                vx=(1 if (t.pos.x - a.pos.x) > 0 else -1) * 420.0,
                vy=-240.0,
                hitstun=0.14,
            ),
            locks_horizontal_movement=False,
            repeated_hit_interval=0.12,
        )
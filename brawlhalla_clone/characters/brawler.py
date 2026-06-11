# characters/brawler.py

from __future__ import annotations
import pygame

from characters.base_character import BaseCharacter
from characters.attack_data import AttackData, HitEffect
from characters.attack_slots import AttackSlot


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
            hit_effect_factory=lambda a, t: HitEffect(
                vx=a.facing * 380.0,
                vy=-760.0,
                hitstun=0.30,
            ),
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
            hit_effect_factory=lambda a, t: HitEffect(
                vx=a.facing * 180.0,
                vy=-120.0,
                hitstun=0.10,
            ),
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
            hit_effect_factory=lambda a, t: HitEffect(
                vx=a.facing * 320.0,
                vy=-560.0,
                hitstun=0.25,
            ),
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
            hit_effect_factory=lambda a, t: HitEffect(
                vx=a.facing * 220.0,
                vy=-720.0,
                hitstun=0.25,
            ),
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
            hit_effect_factory=lambda a, t: HitEffect(
                vx=a.facing * 520.0,
                vy=-420.0,
                hitstun=0.25,
            ),
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
            hit_effect_factory=lambda a, t: HitEffect(
                vx=a.facing * 280.0,
                vy=520.0,
                hitstun=0.25,
            ),
            locks_horizontal_movement=False,
            dash_velocity_x=300.0,
        )
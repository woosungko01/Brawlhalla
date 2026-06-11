from __future__ import annotations
import pygame

from characters.base_character import BaseCharacter
from characters.attack_data import AttackData, HitEffect


class BrawlerCharacter(BaseCharacter):
    character_id = "brawler"

    def resolve_basic_attack(self, fighter) -> AttackData | None:
        if fighter.input.up or fighter.input.down:
            return self._kick()
        elif fighter.input.move_x != 0:
            return self._punch()
        return self._uppercut()

    def try_start_ultimate(self, fighter) -> bool:
        fighter.ultimate_timer = 5.0
        return True

    def _uppercut(self) -> AttackData:
        return AttackData(
            name="brawler_uppercut",
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

    def _punch(self) -> AttackData:
        return AttackData(
            name="brawler_punch",
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

    def _kick(self) -> AttackData:
        return AttackData(
            name="brawler_kick",
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
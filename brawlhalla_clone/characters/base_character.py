from __future__ import annotations
from abc import ABC, abstractmethod
import pygame

from characters.attack_data import AttackData, HitEffect


class BaseCharacter(ABC):
    character_id: str = "base"

    @abstractmethod
    def resolve_basic_attack(self, fighter) -> AttackData | None:
        raise NotImplementedError

    @abstractmethod
    def try_start_ultimate(self, fighter) -> bool:
        raise NotImplementedError

    def get_attack_hitbox(self, fighter) -> pygame.Rect | None:
        if fighter.current_attack is None:
            return None
        return fighter.current_attack.hitbox_factory(fighter)

    def get_hit_effect(self, attacker, target) -> HitEffect:
        if attacker.current_attack is None:
            raise ValueError("No current attack")
        return attacker.current_attack.hit_effect_factory(attacker, target)
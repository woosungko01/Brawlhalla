#characters/base_character

from __future__ import annotations
from abc import ABC, abstractmethod
import pygame

from characters.attack_data import AttackData
from characters.attack_slots import AttackSlot
from combat.knockback import HitEffect


class BaseCharacter(ABC):
    character_id: str = "base"

    def resolve_basic_attack(self, fighter) -> AttackData | None:
        slot = self.resolve_attack_slot(fighter)
        return self.get_attack_for_slot(slot)

    def resolve_attack_slot(self, fighter) -> AttackSlot:
        if fighter.is_grounded:
            if fighter.input.up:
                return AttackSlot.UP
            if fighter.input.down:
                return AttackSlot.DOWN_GROUND
            if fighter.input.move_x != 0:
                return AttackSlot.SIDE
            return AttackSlot.NEUTRAL

        if fighter.input.down:
            return AttackSlot.DOWN_AIR
        if fighter.input.move_x != 0:
            return AttackSlot.SIDE
        return AttackSlot.UP_AIR

    @abstractmethod
    def get_attack_for_slot(self, slot: AttackSlot) -> AttackData | None:
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
        return attacker.current_attack.knockback_model.build_effect(attacker, target)
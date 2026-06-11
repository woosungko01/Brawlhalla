# characters/base_character.py

from __future__ import annotations
from abc import ABC, abstractmethod
import pygame

from characters.attack_data import AttackData, HitEffect
from characters.attack_slots import AttackSlot


class BaseCharacter(ABC):
    character_id: str = "base"

    def resolve_basic_attack(self, fighter) -> AttackData | None:
        slot = self.resolve_attack_slot(fighter)
        return self.get_attack_for_slot(slot)

    def resolve_attack_slot(self, fighter) -> AttackSlot:
        """
        공통 공격 슬롯 해석 규칙

        지상:
        - no input -> neutral
        - left/right -> side
        - up -> up
        - down -> down_ground

        공중:
        - no input -> up_air
        - up -> up_air
        - left/right -> side
        - down -> down_air
        """
        if fighter.is_grounded:
            if fighter.input.up:
                return AttackSlot.UP
            if fighter.input.down:
                return AttackSlot.DOWN_GROUND
            if fighter.input.move_x != 0:
                return AttackSlot.SIDE
            return AttackSlot.NEUTRAL

        # 공중
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
        return attacker.current_attack.hit_effect_factory(attacker, target)
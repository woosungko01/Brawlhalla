# characters/attack_slots.py

from enum import Enum


class AttackSlot(str, Enum):
    NEUTRAL = "neutral"
    SIDE = "side"
    UP = "up"
    UP_AIR = "up_air"
    DOWN_GROUND = "down_ground"
    DOWN_AIR = "down_air"
    ULTIMATE = "ultimate"
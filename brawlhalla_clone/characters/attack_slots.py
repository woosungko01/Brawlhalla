# characters/attack_slots.py

from enum import Enum


class AttackSlot(str, Enum):
    #방향 키에 따라 공격의 종류를 다르게 하기 위한 현재 상태 판별
    NEUTRAL = "neutral"
    SIDE = "side"
    UP = "up"
    UP_AIR = "up_air"
    DOWN_GROUND = "down_ground"
    DOWN_AIR = "down_air"
    ULTIMATE = "ultimate"
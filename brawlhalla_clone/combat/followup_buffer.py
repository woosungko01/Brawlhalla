# combat/followup_buffer.py

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class FollowupAction:
    #공격에 따른 캐릭터의 이동 제어
    action_type: str   # "attack" | "dash"
    move_x: int = 0
    move_y: int = 0
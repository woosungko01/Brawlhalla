# combat/pending_effects.py

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class PendingLaunch:
    vx: float
    vy: float
    hitstun: float
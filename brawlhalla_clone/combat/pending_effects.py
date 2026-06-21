from __future__ import annotations
from dataclasses import dataclass


@dataclass
class PendingLaunch:
    #피격 시 효과(스턴, 밀쳐짐)
    vx: float
    vy: float
    hitstun: float
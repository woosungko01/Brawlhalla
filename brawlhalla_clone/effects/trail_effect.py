from dataclasses import dataclass


@dataclass
class TrailEffect:
    #피격 시 trail 효과
    x: float
    y: float
    lifetime: float
    max_lifetime: float
    scale: float
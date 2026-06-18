from dataclasses import dataclass


@dataclass
class TrailEffect:
    x: float
    y: float
    lifetime: float
    max_lifetime: float
    scale: float
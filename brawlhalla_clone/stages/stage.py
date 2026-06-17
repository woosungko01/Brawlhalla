from dataclasses import dataclass, field
from systems.collision import Platform


@dataclass
class Stage:
    name: str
    world_w: int
    world_h: int

    player_spawn_x: float
    player_spawn_y: float

    dummy_spawn_x: float
    dummy_spawn_y: float

    background_path: str | None = None

    platforms: list[Platform] = field(default_factory=list)
# stages/stage.py

from dataclasses import dataclass, field
from systems.collision import Platform


@dataclass
class Stage:
    """
    스테이지 데이터 컨테이너.

    앞으로 스테이지 종류가 많아질 걸 고려해서
    월드 크기, 스폰 위치, 플랫폼 목록 등을 한 곳에 묶는다.
    """
    name: str
    world_w: int
    world_h: int

    player_spawn_x: float
    player_spawn_y: float

    dummy_spawn_x: float
    dummy_spawn_y: float

    platforms: list[Platform] = field(default_factory=list)
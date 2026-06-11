# stages/test_stage.py

from stages.stage import Stage
from systems.collision import Platform


def build_test_stage() -> Stage:
    world_w = 3200
    world_h = 1800

    floor_y = 1760
    floor_h = 40

    return Stage(
        name="test_stage",
        world_w=world_w,
        world_h=world_h,

        player_spawn_x=300.0,
        player_spawn_y=1400.0,

        dummy_spawn_x=world_w / 2,
        dummy_spawn_y=floor_y - floor_h - 36,

        platforms=[
            Platform(0, 1760, 3200, 40),

            Platform(150, 1500, 250, 20),
            Platform(450, 1380, 220, 20),
            Platform(120, 1220, 180, 20),

            Platform(700, 1450, 300, 20),
            Platform(1100, 1300, 260, 20),
            Platform(900, 1120, 220, 20),
            Platform(1400, 980, 250, 20),

            Platform(1900, 1500, 280, 20),
            Platform(2300, 1360, 240, 20),
            Platform(2600, 1200, 220, 20),
            Platform(2900, 1020, 180, 20),

            Platform(1650, 1600, 180, 20),
            Platform(2100, 1180, 160, 20),
            Platform(2500, 900, 150, 20),
        ],
    )
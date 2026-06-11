# stages/test_stage.py

from stages.stage import Stage
from systems.collision import Platform


def build_test_stage() -> Stage:
    world_w = 2400
    world_h = 1400

    # 메인 플랫폼
    main_x = 700
    main_y = 900
    main_w = 1000
    main_h = 260

    # 위쪽 소형 플랫폼 2개
    soft_w = 220
    soft_h = 20
    soft_y = 620

    left_soft_x = 780
    right_soft_x = 1400

    player_spawn_x = main_x + 350
    player_spawn_y = main_y - 80

    dummy_spawn_x = main_x + main_w - 350
    dummy_spawn_y = main_y - 80

    return Stage(
        name="test_stage",
        world_w=world_w,
        world_h=world_h,

        player_spawn_x=player_spawn_x,
        player_spawn_y=player_spawn_y,

        dummy_spawn_x=dummy_spawn_x,
        dummy_spawn_y=dummy_spawn_y,

        platforms=[
            # 메인 플랫폼
            Platform(main_x, main_y, main_w, main_h),

            # 위 소형 플랫폼 2개
            Platform(left_soft_x, soft_y, soft_w, soft_h),
            Platform(right_soft_x, soft_y, soft_w, soft_h),
        ],
    )
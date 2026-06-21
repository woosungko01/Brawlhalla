from stages.stage import Stage
from systems.collision import Platform


def build_test_stage() -> Stage:
    """
    새 배경 스테이지.
    초록 경계를 기준으로 플랫폼을 수동 배치한다.

    원본 배경 이미지 기준 해상도:
    1920 x 1080

    월드도 같은 크기로 맞춤.
    """
    world_w = 1920
    world_h = 1080

    # 메인 플랫폼 상단 기준 대략 좌표
    # 표시선 기준으로 직접 맞춘 값
    main_x = 621
    main_y = 612
    main_w = 674
    main_h = 185

    # 소프트 플랫폼 3개
    top_soft_x = 859
    top_soft_y = 392
    top_soft_w = 195
    top_soft_h = 20

    left_soft_x = 639
    left_soft_y = 478
    left_soft_w = 205
    left_soft_h = 20

    right_soft_x = 1084
    right_soft_y = 476
    right_soft_w = 205
    right_soft_h = 20

    # 스폰 위치
    player_spawn_x = 830
    player_spawn_y = main_y - 90

    dummy_spawn_x = 1080
    dummy_spawn_y = main_y - 90

    return Stage(
        name="temple_stage",
        world_w=world_w,
        world_h=world_h,

        player_spawn_x=player_spawn_x,
        player_spawn_y=player_spawn_y,

        dummy_spawn_x=dummy_spawn_x,
        dummy_spawn_y=dummy_spawn_y,

        background_path="assets/stages/temple_stage.png",

        platforms=[
            Platform(main_x, main_y, main_w, main_h, is_soft=False),

            Platform(top_soft_x, top_soft_y, top_soft_w, top_soft_h, is_soft=True),
            Platform(left_soft_x, left_soft_y, left_soft_w, left_soft_h, is_soft=True),
            Platform(right_soft_x, right_soft_y, right_soft_w, right_soft_h, is_soft=True),
        ],
    )
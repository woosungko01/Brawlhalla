# systems/gravity.py
#
# 중력 + 패스트폴 처리.
#
# 정책:
# - 지상에서는 중력을 적용하지 않음
# - 점프 직후 아주 짧은 시간 동안 fast fall 금지
# - fast fall은 추가 중력으로 더 빨리 하강시키되,
#   종단속도는 별도로 제한

from core.player import Player


def apply_vertical_forces(player: Player, dt: float) -> None:
    if player.is_grounded:
        if player.vel.y > 0:
            player.vel.y = 0.0
        player.fast_falling = False
        return

    cfg = player.gravity_cfg

    wants_fast_fall = bool(player.input.down)  # type: ignore[attr-defined]
    can_fast_fall = player.fast_fall_lock_timer <= 0.0

    # wall cling 중에는 fast fall 불가
    if player.is_wall_clinging:
        player.fast_falling = False
    else:
        player.fast_falling = wants_fast_fall and can_fast_fall

    gravity = cfg.GRAVITY
    max_fall_speed = cfg.MAX_FALL_SPEED

    if player.fast_falling:
        gravity += cfg.FAST_FALL_ACCEL_BONUS
        max_fall_speed = cfg.FAST_FALL_TERMINAL_SPEED

    player.vel.y += gravity * dt

    if player.vel.y > max_fall_speed:
        player.vel.y = max_fall_speed

    # 벽 슬라이드 속도 제한
    if player.is_wall_clinging and player.vel.y > cfg.WALL_SLIDE_SPEED:
        player.vel.y = cfg.WALL_SLIDE_SPEED
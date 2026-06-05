# systems/movement.py
#
# 수평 이동 처리.
# 대시 중일 때는 이 시스템을 건너뛰고 dash.py가 처리한다.

from core.player import Player


def _move_toward(value: float, target: float, max_delta: float) -> float:
    """value를 target 방향으로 최대 max_delta만큼 이동"""
    if value < target:
        return min(value + max_delta, target)
    elif value > target:
        return max(value - max_delta, target)
    return value


def apply_horizontal_control(player: Player, dt: float) -> None:
    """
    좌우 입력에 따라 vel.x를 갱신.
    대시 시스템이 활성화 중이면 호출하지 않는다.
    """
    cfg = player.move_cfg
    move_x = player.input.move_x   # type: ignore[attr-defined]  # input은 update에서 주입

    # 방향 갱신
    if move_x != 0:
        player.facing = move_x

    if player.is_grounded:
        accel    = cfg.GROUND_ACCEL
        friction = cfg.GROUND_FRICTION
        max_spd  = cfg.MAX_RUN_SPEED
    else:
        accel    = cfg.AIR_ACCEL
        friction = cfg.AIR_DRAG
        max_spd  = cfg.MAX_AIR_SPEED

    if move_x != 0:
        target = move_x * max_spd
        player.vel.x = _move_toward(player.vel.x, target, accel * dt)
    else:
        player.vel.x = _move_toward(player.vel.x, 0.0, friction * dt)

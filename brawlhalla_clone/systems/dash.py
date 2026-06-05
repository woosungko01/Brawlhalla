from core.player import Player


def tick_dash_timers(player: Player, dt: float) -> None:
    if player.dash_reuse_timer > 0.0:
        player.dash_reuse_timer = max(0.0, player.dash_reuse_timer - dt)


def try_request_dash(player: Player) -> None:
    """
    dash 입력이 들어온 그 순간에만 판정.
    가능하면 즉시 dash 시작, 불가능하면 버림.
    """
    move_x = player.input.move_x  # type: ignore[attr-defined]

    if move_x == 0:
        return

    if player.is_dashing:
        return

    # 지상 또는 near-ground가 아니면 dash 불가
    if not player.is_grounded and not player.near_ground:
        return

    # dash 이후 아직 공중을 거치지 않았고, reuse 제한 중이면 불가
    if player.dash_reuse_timer > 0.0 and not player.left_ground_since_dash:
        return

    _begin_dash(player, move_x)


def _begin_dash(player: Player, direction: int) -> None:
    player.is_dashing = True
    player.dash_timer = player.dash_cfg.DASH_TIME
    player.dash_dir = direction
    player.facing = direction

    player.vel.x = direction * player.dash_cfg.DASH_SPEED
    player.vel.y = 0.0
    player.is_grounded = True

    # dash 시작 직후엔 아직 공중을 안 거친 상태
    player.left_ground_since_dash = False

    # 기본적으로 지상 연속 dash 제한 시작
    player.dash_reuse_timer = player.dash_cfg.GROUND_CHAIN_REUSE


def update_dash(player: Player, dt: float) -> None:
    if not player.is_dashing:
        return

    player.dash_timer -= dt
    player.vel.x = player.dash_dir * player.dash_cfg.DASH_SPEED
    player.vel.y = 0.0

    if player.dash_timer <= 0.0:
        _end_dash(player)


def _end_dash(player: Player) -> None:
    old_dir = player.dash_dir

    player.is_dashing = False
    player.dash_timer = 0.0
    player.dash_dir = 0

    move_x = player.input.move_x  # type: ignore[attr-defined]
    if move_x == old_dir:
        player.vel.x = old_dir * player.dash_cfg.SPRINT_SPEED
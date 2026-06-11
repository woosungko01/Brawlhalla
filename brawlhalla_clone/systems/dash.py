# systems/dash.py

from entities.fighter import Fighter


def tick_dash_timers(fighter: Fighter, dt: float) -> None:
    if fighter.dash_reuse_timer > 0.0:
        fighter.dash_reuse_timer = max(0.0, fighter.dash_reuse_timer - dt)


def try_request_dash(fighter: Fighter) -> None:
    """
    dash 입력이 들어온 그 순간에만 판정.
    가능하면 즉시 dash 시작, 불가능하면 버림.

    정책:
    - 기본 dash는 지상에서만 가능
    - 공중 snap dash는 상위 로직에서 snap_to_ground() 성공 후 다시 이 함수를 호출해서 처리
    """
    move_x = fighter.input.move_x

    if move_x == 0:
        return

    if fighter.is_dashing:
        return

    # 기본적으로 지상에서만 dash 허용
    if not fighter.is_grounded:
        return

    if fighter.dash_reuse_timer > 0.0 and not fighter.left_ground_since_dash:
        return

    _begin_dash(fighter, move_x)


def _begin_dash(fighter: Fighter, direction: int) -> None:
    fighter.is_dashing = True
    fighter.dash_timer = fighter.dash_cfg.DASH_TIME
    fighter.dash_dir = direction
    fighter.facing = direction

    fighter.vel.x = direction * fighter.dash_cfg.DASH_SPEED
    fighter.vel.y = 0.0
    fighter.is_grounded = True

    fighter.left_ground_since_dash = False
    fighter.dash_reuse_timer = fighter.dash_cfg.GROUND_CHAIN_REUSE


def update_dash(fighter: Fighter, dt: float) -> None:
    if not fighter.is_dashing:
        return

    fighter.dash_timer -= dt
    fighter.vel.x = fighter.dash_dir * fighter.dash_cfg.DASH_SPEED
    fighter.vel.y = 0.0

    if fighter.dash_timer <= 0.0:
        _end_dash(fighter)


def _end_dash(fighter: Fighter) -> None:
    old_dir = fighter.dash_dir

    fighter.is_dashing = False
    fighter.dash_timer = 0.0
    fighter.dash_dir = 0

    move_x = fighter.input.move_x
    if move_x == old_dir:
        fighter.vel.x = old_dir * fighter.dash_cfg.SPRINT_SPEED
# systems/jump.py

from entities.fighter import Fighter


def can_request_jump(fighter: Fighter) -> bool:
    """현재 점프를 예약할 수 있는가"""
    if fighter.is_dodging:
        return False

    if fighter.jump_startup_timer > 0:
        return False

    if fighter.pending_jump_kind is not None:
        return False

    if fighter.is_grounded:
        return True

    return fighter.air.jumps_used < fighter.jump_cfg.MAX_AIR_JUMPS


def try_request_jump(fighter: Fighter) -> None:
    """점프 입력이 왔을 때 호출. 조건을 검사하고 startup을 시작한다."""
    if not can_request_jump(fighter):
        return

    fighter.pending_jump_kind = "ground" if fighter.is_grounded else "air"
    fighter.jump_startup_timer = fighter.jump_cfg.JUMP_STARTUP_TIME


def execute_pending_jump(fighter: Fighter) -> None:
    """
    startup 타이머가 0이 되면 실제 점프를 발동.
    tick_timers() 이후에 호출해야 한다.
    """
    if fighter.jump_startup_timer > 0.0:
        return
    if fighter.pending_jump_kind is None:
        return

    _do_jump(fighter, fighter.pending_jump_kind)
    fighter.pending_jump_kind = None


def _do_jump(fighter: Fighter, kind: str) -> None:
    fighter.vel.y = -fighter.jump_cfg.JUMP_SPEED
    fighter.is_grounded = False
    fighter.fast_falling = False

    fighter.fast_fall_lock_timer = fighter.jump_cfg.FAST_FALL_LOCK_TIME

    if fighter.is_dashing:
        fighter.is_dashing = False
        fighter.dash_timer = 0.0
        fighter.dash_dir = 0

    if kind == "air":
        fighter.air.consume_jump()

    fighter.is_wall_clinging = False
    fighter.was_wall_clinging = False
    fighter.wall_dir = 0
    fighter.wall_detach_grace_timer = 0.0
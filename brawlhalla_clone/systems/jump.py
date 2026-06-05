# systems/jump.py
#
# 점프 흐름:
#   1. 입력 → try_request_jump() → pending_jump_kind 세팅 + startup 타이머 시작
#   2. startup 완료 → execute_pending_jump() → 실제 vel.y 변경
#
# 이렇게 "예약 → 발동" 2단계로 나누어야 나중에
# 공격 중 점프 예외, 피격 중 점프 차단 등을 깔끔하게 처리할 수 있다.

from core.player import Player


# ── 판정 함수 ─────────────────────────────────────────────────────────────


def can_request_jump(player: Player) -> bool:
    """현재 점프를 예약할 수 있는가"""
    if player.landing_recovery_timer > 0.0:
        return False

    if player.jump_startup_timer > 0:
        return False

    if player.pending_jump_kind is not None:
        return False

    if player.is_grounded:
        return True

    return player.air.jumps_used < player.jump_cfg.MAX_AIR_JUMPS


# ── 요청 → 예약 ──────────────────────────────────────────────────────────


def try_request_jump(player: Player) -> None:
    """점프 입력이 왔을 때 호출. 조건을 검사하고 startup을 시작한다."""
    if not can_request_jump(player):
        return

    player.pending_jump_kind = "ground" if player.is_grounded else "air"
    player.jump_startup_timer = player.jump_cfg.JUMP_STARTUP_TIME


# ── startup 완료 → 실제 점프 ─────────────────────────────────────────────


def execute_pending_jump(player: Player) -> None:
    """
    startup 타이머가 0이 되면 실제 점프를 발동.
    tick_timers() 이후에 호출해야 한다.
    """
    if player.jump_startup_timer > 0.0:
        return
    if player.pending_jump_kind is None:
        return

    _do_jump(player, player.pending_jump_kind)
    player.pending_jump_kind = None


def _do_jump(player: Player, kind: str) -> None:
    player.vel.y = -player.jump_cfg.JUMP_SPEED
    player.is_grounded = False
    player.fast_falling = False

    # 점프 직후 아주 짧은 시간 동안 fast fall 금지
    player.fast_fall_lock_timer = player.jump_cfg.FAST_FALL_LOCK_TIME

    # 점프 시 dash 관련 상태 정리
    # dash jump는 active dash의 수평속도는 이미 vel.x에 남아 있으므로 유지됨
    if player.is_dashing:
        player.is_dashing = False
        player.dash_timer = 0.0
        player.dash_dir = 0

    # startup 상태의 dash도 취소
    player.dash_startup_timer = 0.0
    player.dash_start_dir = 0

    if kind == "air":
        player.air.consume_jump()
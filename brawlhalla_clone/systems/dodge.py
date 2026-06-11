# systems/dodge.py

from __future__ import annotations
import math

from entities.fighter import Fighter


SPOT_DODGE = "spot"
MOVE_DODGE = "move"


def tick_dodge_timers(fighter: Fighter, dt: float) -> None:
    if fighter.dodge_timer > 0.0:
        fighter.dodge_timer = max(0.0, fighter.dodge_timer - dt)

    if fighter.invuln_timer > 0.0:
        fighter.invuln_timer = max(0.0, fighter.invuln_timer - dt)


def can_start_dodge(fighter: Fighter) -> bool:
    if fighter.is_dashing:
        return False
    if fighter.is_dodging:
        return False
    if fighter.jump_startup_timer > 0.0:
        return False
    if fighter.stun_timer > 0.0:
        return False
    return True


def try_request_dodge(fighter: Fighter) -> bool:
    """
    dodge 버튼 입력 시 호출.
    - 지상 + 무방향 -> spot dodge
    - 지상 + 방향 입력 -> dodge 아님 (상위에서 dash 처리)
    - 공중 + 무방향 -> air spot dodge
    - 공중 + 방향 입력 -> air directional dodge
    성공 시 True
    """
    if not can_start_dodge(fighter):
        return False

    move_x = fighter.input.move_x
    move_y = int(fighter.input.down) - int(fighter.input.up)

    # 지상
    if fighter.is_grounded:
        if move_x == 0 and move_y == 0:
            _begin_spot_dodge(fighter)
            return True
        return False

    # 공중
    if not fighter.air_dodge_available:
        return False

    if move_x == 0 and move_y == 0:
        _begin_spot_dodge(fighter)
        fighter.air_dodge_available = False
        return True

    _begin_directional_dodge(fighter, move_x, move_y)
    fighter.air_dodge_available = False
    return True


def _begin_spot_dodge(fighter: Fighter) -> None:
    fighter.is_dodging = True
    fighter.dodge_kind = SPOT_DODGE
    fighter.dodge_timer = fighter.dodge_cfg.SPOT_DODGE_TIME

    fighter.dodge_dir_x = 0.0
    fighter.dodge_dir_y = 0.0

    fighter.vel.x = 0.0
    fighter.vel.y = 0.0

    fighter.invuln_timer = fighter.dodge_cfg.SPOT_DODGE_INVULN_TIME


def _begin_directional_dodge(fighter: Fighter, move_x: int, move_y: int) -> None:
    fighter.is_dodging = True
    fighter.dodge_kind = MOVE_DODGE
    fighter.dodge_timer = fighter.dodge_cfg.AIR_DODGE_TIME

    length = math.sqrt(move_x * move_x + move_y * move_y)
    if length <= 0.0:
        fighter.dodge_dir_x = 0.0
        fighter.dodge_dir_y = 0.0
    else:
        fighter.dodge_dir_x = move_x / length
        fighter.dodge_dir_y = move_y / length

    fighter.invuln_timer = fighter.dodge_cfg.AIR_DODGE_INVULN_TIME

    fighter.vel.x = fighter.dodge_dir_x * fighter.dodge_cfg.AIR_DODGE_SPEED
    fighter.vel.y = fighter.dodge_dir_y * fighter.dodge_cfg.AIR_DODGE_SPEED


def update_dodge(fighter: Fighter, dt: float) -> None:
    if not fighter.is_dodging:
        return

    if fighter.dodge_kind == SPOT_DODGE:
        fighter.vel.x = 0.0
        fighter.vel.y = 0.0

    elif fighter.dodge_kind == MOVE_DODGE:
        fighter.vel.x = fighter.dodge_dir_x * fighter.dodge_cfg.AIR_DODGE_SPEED
        fighter.vel.y = fighter.dodge_dir_y * fighter.dodge_cfg.AIR_DODGE_SPEED

    if fighter.dodge_timer <= 0.0:
        end_dodge(fighter)


def cancel_dodge(fighter: Fighter) -> None:
    if not fighter.is_dodging:
        return

    fighter.is_dodging = False
    fighter.dodge_kind = None
    fighter.dodge_timer = 0.0
    fighter.dodge_dir_x = 0.0
    fighter.dodge_dir_y = 0.0


def end_dodge(fighter: Fighter) -> None:
    cancel_dodge(fighter)

    # 공중 directional dodge 끝난 뒤 속도를 약간 남길지 여부는 취향
    # 지금은 자동 종료 후 현재 vel 유지 대신 0으로 정리
    fighter.vel.x = 0.0
    if fighter.is_grounded:
        fighter.vel.y = 0.0
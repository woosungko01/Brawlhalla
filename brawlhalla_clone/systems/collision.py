# systems/collision.py
#
# 충돌 감지 + grounded 판정 + 착지 이벤트.
#
# 설계 포인트:
# - 이동과 충돌 해결은 move_and_collide()가 담당
# - grounded 판정은 "충돌 결과"가 아니라 발 아래 probe 검사로 유지
# - 착지 순간에는 공중 자원 리셋, landing recovery 시작
# - 안전장치로 착지 시 대시 상태도 종료
# - 벽/천장 접촉 상태를 fighter에 반영

from __future__ import annotations
from dataclasses import dataclass
from typing import List

import pygame

from entities.fighter import Fighter


@dataclass
class Platform:
    """사각형 플랫폼 데이터"""
    x: float
    y: float
    width: float
    height: float

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x),
            int(self.y),
            int(self.width),
            int(self.height),
        )


@dataclass
class CollisionResult:
    on_ground: bool = False
    hit_ceiling: bool = False
    hit_left_wall: bool = False
    hit_right_wall: bool = False


def move_and_collide(
    fighter: Fighter,
    dt: float,
    platforms: List[Platform],
) -> CollisionResult:
    result = CollisionResult()

    fighter.touching_wall = False
    fighter.touching_ceiling = False
    fighter.wall_dir = 0

    # 수평 이동
    fighter.pos.x += fighter.vel.x * dt
    p_rect = _fighter_rect(fighter)

    for platform in platforms:
        plat = platform.rect
        if not p_rect.colliderect(plat):
            continue

        if fighter.pos.x < plat.centerx:
            fighter.pos.x = plat.left - fighter.width / 2
            result.hit_right_wall = True
            fighter.wall_dir = 1
        else:
            fighter.pos.x = plat.right + fighter.width / 2
            result.hit_left_wall = True
            fighter.wall_dir = -1

        fighter.vel.x = 0.0
        fighter.touching_wall = True
        p_rect = _fighter_rect(fighter)

    # 수직 이동
    fighter.pos.y += fighter.vel.y * dt
    p_rect = _fighter_rect(fighter)

    for platform in platforms:
        plat = platform.rect
        if not p_rect.colliderect(plat):
            continue

        if fighter.pos.y < plat.centery:
            fighter.pos.y = plat.top - fighter.height / 2
            result.on_ground = True
        else:
            fighter.pos.y = plat.bottom + fighter.height / 2
            result.hit_ceiling = True
            fighter.touching_ceiling = True

        fighter.vel.y = 0.0
        p_rect = _fighter_rect(fighter)

    return result


def update_grounded(fighter: Fighter, platforms: List[Platform]) -> None:
    """
    grounded와 near_ground를 동시에 갱신.
    - grounded: 발 바로 아래 짧은 probe
    - near_ground: 발 아래 좀 더 긴 probe (dash snap 용)
    """
    GROUND_PROBE_PX = 3
    near_ground_px = int(fighter.dash_cfg.GROUND_SNAP_DIST)

    grounded_probe = pygame.Rect(
        int(fighter.rect_x) + 2,
        int(fighter.bottom),
        max(1, fighter.width - 4),
        GROUND_PROBE_PX,
    )

    near_ground_probe = pygame.Rect(
        int(fighter.rect_x) + 2,
        int(fighter.bottom),
        max(1, fighter.width - 4),
        max(GROUND_PROBE_PX, near_ground_px),
    )

    fighter.is_grounded = any(
        grounded_probe.colliderect(platform.rect) for platform in platforms
    )

    fighter.near_ground = any(
        near_ground_probe.colliderect(platform.rect) for platform in platforms
    )


def handle_landing(fighter: Fighter) -> None:
    if fighter.was_grounded or not fighter.is_grounded:
        return

    fighter.fast_falling = False
    fighter.air.reset()
    fighter.landing_recovery_timer = fighter.jump_cfg.LANDING_RECOVERY_TIME

    fighter.left_ground_since_dash = True

    fighter.is_dashing = False
    fighter.dash_timer = 0.0
    fighter.dash_dir = 0

    fighter.is_wall_clinging = False
    fighter.was_wall_clinging = False
    fighter.wall_dir = 0
    fighter.wall_detach_grace_timer = 0.0


def _fighter_rect(fighter: Fighter) -> pygame.Rect:
    return pygame.Rect(
        int(fighter.rect_x),
        int(fighter.rect_y),
        fighter.width,
        fighter.height,
    )


def snap_to_ground(fighter: Fighter, platforms: List[Platform]) -> bool:
    """
    fighter가 near_ground 상태일 때 가장 가까운 아래 플랫폼 위로 붙인다.
    성공하면 True.
    """
    best_top = None
    foot_x1 = fighter.left + 2
    foot_x2 = fighter.right - 2

    for platform in platforms:
        plat = platform.rect

        if foot_x2 <= plat.left or foot_x1 >= plat.right:
            continue

        if plat.top < fighter.bottom:
            continue

        dist = plat.top - fighter.bottom
        if dist < 0 or dist > fighter.dash_cfg.GROUND_SNAP_DIST:
            continue

        if best_top is None or plat.top < best_top:
            best_top = plat.top

    if best_top is None:
        return False

    fighter.pos.y = best_top - fighter.height / 2
    fighter.vel.y = 0.0
    fighter.is_grounded = True
    return True


def update_wall_cling(fighter: Fighter) -> None:
    """
    wall cling은 한 번 진입하면 latch 상태로 유지된다.
    - 입력 없이도 유지
    - 실제 벽 접촉이 잠깐 끊겨도 grace 시간 동안 유지
    - 해제는 별도 입력/상태 함수에서 처리
    """
    if fighter.is_wall_clinging:
        if fighter.is_grounded:
            fighter.is_wall_clinging = False
            fighter.wall_dir = 0
            fighter.wall_detach_grace_timer = 0.0
            return

        if fighter.touching_wall:
            fighter.wall_detach_grace_timer = fighter.gravity_cfg.WALL_DETACH_GRACE_TIME
            return

        if fighter.wall_detach_grace_timer > 0.0:
            return

        fighter.is_wall_clinging = False
        fighter.wall_dir = 0
        return

    if (
        not fighter.is_grounded
        and fighter.touching_wall
        and fighter.vel.y >= 0.0
    ):
        fighter.is_wall_clinging = True
        fighter.wall_detach_grace_timer = fighter.gravity_cfg.WALL_DETACH_GRACE_TIME


def handle_wall_touch(fighter: Fighter) -> None:
    """
    wall cling 상태에 새로 진입한 순간 한 번만 실행.
    air resources를 회복한다.
    """
    if not fighter.was_wall_clinging and fighter.is_wall_clinging:
        fighter.air.reset()

    fighter.was_wall_clinging = fighter.is_wall_clinging


def handle_wall_detach_inputs(fighter: Fighter) -> None:
    if not fighter.is_wall_clinging:
        return

    move_x = fighter.input.move_x

    if move_x != 0 and move_x != fighter.wall_dir:
        fighter.is_wall_clinging = False
        fighter.wall_detach_grace_timer = 0.0
        return

    if fighter.input.down:
        fighter.is_wall_clinging = False
        fighter.wall_detach_grace_timer = 0.0
        return

    if fighter.input.attack_pressed:
        fighter.is_wall_clinging = False
        fighter.wall_detach_grace_timer = 0.0
        return

    if fighter.input.dodge_pressed:
        fighter.is_wall_clinging = False
        fighter.wall_detach_grace_timer = 0.0
        return

    if fighter.input.jump_pressed:
        fighter.is_wall_clinging = False
        fighter.wall_detach_grace_timer = 0.0
        return
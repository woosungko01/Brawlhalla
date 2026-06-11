# systems/collision.py
#
# 충돌 감지 + grounded 판정 + 착지 이벤트.
#
# 설계 포인트:
# - 이동과 충돌 해결은 move_and_collide()가 담당
# - grounded 판정은 "충돌 결과"가 아니라 발 아래 probe 검사로 유지
# - 착지 순간에는 공중 자원 리셋, landing recovery 시작
# - 안전장치로 착지 시 대시 상태도 종료
# - 벽/천장 접촉 상태를 player에 반영

from __future__ import annotations
from dataclasses import dataclass
from typing import List

import pygame

from core.player import Player


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


# ── 이동 + 충돌 해결 ──────────────────────────────────────────────────────

def move_and_collide(
    player: Player,
    dt: float,
    platforms: List[Platform],
) -> CollisionResult:
    result = CollisionResult()

    # 프레임 시작 시 접촉 상태 초기화
    player.touching_wall = False
    player.touching_ceiling = False
    player.wall_dir = 0

    # ── 수평 이동 ──────────────────────────────────────────
    player.pos.x += player.vel.x * dt
    p_rect = _player_rect(player)

    for platform in platforms:
        plat = platform.rect
        if not p_rect.colliderect(plat):
            continue

        # 플레이어 중심이 플랫폼 중심보다 왼쪽이면
        # 플레이어의 오른쪽 면이 플랫폼의 왼쪽 면에 닿은 상황
        if player.pos.x < plat.centerx:
            player.pos.x = plat.left - player.width / 2
            result.hit_right_wall = True
            player.wall_dir = 1  # 벽이 플레이어 오른쪽에 있음
        else:
            player.pos.x = plat.right + player.width / 2
            result.hit_left_wall = True
            player.wall_dir = -1  # 벽이 플레이어 왼쪽에 있음

        player.vel.x = 0.0
        player.touching_wall = True
        p_rect = _player_rect(player)

    # ── 수직 이동 ──────────────────────────────────────────
    player.pos.y += player.vel.y * dt
    p_rect = _player_rect(player)

    for platform in platforms:
        plat = platform.rect
        if not p_rect.colliderect(plat):
            continue

        # 플레이어 중심이 플랫폼 중심보다 위면 착지 처리
        if player.pos.y < plat.centery:
            player.pos.y = plat.top - player.height / 2
            result.on_ground = True
        else:
            # 머리가 천장에 닿은 경우
            player.pos.y = plat.bottom + player.height / 2
            result.hit_ceiling = True
            player.touching_ceiling = True

        player.vel.y = 0.0
        p_rect = _player_rect(player)

    return result


# ── grounded 판정: 발 아래 probe 검사 ────────────────────────────────────

def update_grounded(player: Player, platforms: List[Platform]) -> None:
    """
    grounded와 near_ground를 동시에 갱신.
    - grounded: 발 바로 아래 짧은 probe
    - near_ground: 발 아래 좀 더 긴 probe (dash snap 용)
    """
    GROUND_PROBE_PX = 3
    near_ground_px = int(player.dash_cfg.GROUND_SNAP_DIST)

    grounded_probe = pygame.Rect(
        int(player.rect_x) + 2,
        int(player.bottom),
        max(1, player.width - 4),
        GROUND_PROBE_PX,
    )

    near_ground_probe = pygame.Rect(
        int(player.rect_x) + 2,
        int(player.bottom),
        max(1, player.width - 4),
        max(GROUND_PROBE_PX, near_ground_px),
    )

    player.is_grounded = any(
        grounded_probe.colliderect(platform.rect) for platform in platforms
    )

    player.near_ground = any(
        near_ground_probe.colliderect(platform.rect) for platform in platforms
    )

# ── 착지 이벤트 ───────────────────────────────────────────────────────────

def handle_landing(player: Player) -> None:
    if player.was_grounded or not player.is_grounded:
        return

    player.fast_falling = False
    player.air.reset()
    player.landing_recovery_timer = player.jump_cfg.LANDING_RECOVERY_TIME

    player.left_ground_since_dash = True

    player.is_dashing = False
    player.dash_timer = 0.0
    player.dash_dir = 0

    player.is_wall_clinging = False
    player.was_wall_clinging = False
    player.wall_dir = 0
    player.wall_detach_grace_timer = 0.0

# ── 내부 헬퍼 ─────────────────────────────────────────────────────────────

def _player_rect(player: Player) -> pygame.Rect:
    return pygame.Rect(
        int(player.rect_x),
        int(player.rect_y),
        player.width,
        player.height,
    )

# ── SnapToGround ─────────────────────────────────────────────────────────────

def snap_to_ground(player: Player, platforms: List[Platform]) -> bool:
    """
    플레이어가 near_ground 상태일 때 가장 가까운 아래 플랫폼 위로 붙인다.
    성공하면 True.
    """
    best_top = None
    foot_x1 = player.left + 2
    foot_x2 = player.right - 2

    for platform in platforms:
        plat = platform.rect

        # 수평으로 플레이어 발 위치와 겹치는지
        if foot_x2 <= plat.left or foot_x1 >= plat.right:
            continue

        # 플레이어 발 아래쪽에 있는 플랫폼만 후보
        if plat.top < player.bottom:
            continue

        dist = plat.top - player.bottom
        if dist < 0 or dist > player.dash_cfg.GROUND_SNAP_DIST:
            continue

        if best_top is None or plat.top < best_top:
            best_top = plat.top

    if best_top is None:
        return False

    player.pos.y = best_top - player.height / 2
    player.vel.y = 0.0
    player.is_grounded = True
    return True

def update_wall_cling(player: Player) -> None:
    """
    wall cling은 한 번 진입하면 latch 상태로 유지된다.
    - 입력 없이도 유지
    - 실제 벽 접촉이 잠깐 끊겨도 grace 시간 동안 유지
    - 해제는 별도 입력/상태 함수에서 처리
    """
    if player.is_wall_clinging:
        if player.is_grounded:
            player.is_wall_clinging = False
            player.wall_dir = 0
            player.wall_detach_grace_timer = 0.0
            return

        if player.touching_wall:
            player.wall_detach_grace_timer = player.gravity_cfg.WALL_DETACH_GRACE_TIME
            return

        if player.wall_detach_grace_timer > 0.0:
            return

        player.is_wall_clinging = False
        player.wall_dir = 0
        return

    # 새 진입
    if (
        not player.is_grounded
        and player.touching_wall
        and player.vel.y >= 0.0
    ):
        player.is_wall_clinging = True
        player.wall_detach_grace_timer = player.gravity_cfg.WALL_DETACH_GRACE_TIME

def handle_wall_touch(player: Player) -> None:
    """
    wall cling 상태에 새로 진입한 순간 한 번만 실행.
    air resources를 회복한다.
    """
    if not player.was_wall_clinging and player.is_wall_clinging:
        player.air.reset()

    player.was_wall_clinging = player.is_wall_clinging


def handle_wall_detach_inputs(player: Player) -> None:
    if not player.is_wall_clinging:
        return

    move_x = player.input.move_x

    # 벽 반대 방향 입력이면 해제
    if move_x != 0 and move_x != player.wall_dir:
        player.is_wall_clinging = False
        player.wall_detach_grace_timer = 0.0
        return

    # 아래 입력(패스트폴 의도)
    if player.input.down:
        player.is_wall_clinging = False
        player.wall_detach_grace_timer = 0.0
        return

    # 점프 / 공격 / 대시도 해제
    if player.input.attack_pressed:
        player.is_wall_clinging = False
        player.wall_detach_grace_timer = 0.0
        return

    if player.input.dodge_pressed:
        player.is_wall_clinging = False
        player.wall_detach_grace_timer = 0.0
        return

    if player.input.jump_pressed:
        player.is_wall_clinging = False
        player.wall_detach_grace_timer = 0.0
        return
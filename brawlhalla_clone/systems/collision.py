# systems/collision.py

from __future__ import annotations
from dataclasses import dataclass
from typing import List

import pygame

from entities.fighter import Fighter


@dataclass
class Platform:
    x: float
    y: float
    width: float
    height: float
    is_soft: bool = False

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

    prev_x = fighter.pos.x
    prev_y = fighter.pos.y
    prev_bottom = fighter.bottom

    # ── 수평 이동 ──
    fighter.pos.x += fighter.vel.x * dt
    p_rect = _fighter_rect(fighter)

    for platform in platforms:
        if platform.is_soft:
            continue  # soft platform은 옆면 충돌 없음

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

    # ── 수직 이동 ──
    fighter.pos.y += fighter.vel.y * dt
    p_rect = _fighter_rect(fighter)
    current_bottom = fighter.bottom
    current_top = fighter.top

    for platform in platforms:
        plat = platform.rect

        if platform.is_soft:
            if _should_land_on_soft_platform(
                fighter,
                platform,
                prev_bottom,
                current_bottom,
            ):
                fighter.pos.y = plat.top - fighter.height / 2
                fighter.vel.y = 0.0
                result.on_ground = True
                p_rect = _fighter_rect(fighter)
            continue

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


def _should_land_on_soft_platform(
    fighter: Fighter,
    platform: Platform,
    prev_bottom: float,
    current_bottom: float,
) -> bool:
    if fighter.drop_through_timer > 0.0:
        return False

    if fighter.vel.y < 0.0:
        return False

    plat = platform.rect

    # 수평으로 겹쳐야 함
    foot_left = fighter.left + 2
    foot_right = fighter.right - 2
    if foot_right <= plat.left or foot_left >= plat.right:
        return False

    # 이전 프레임 발은 플랫폼 위쪽, 현재 발은 플랫폼 top을 지나거나 닿아야 함
    if prev_bottom > plat.top:
        return False

    if current_bottom < plat.top:
        return False

    return True


def update_grounded(fighter: Fighter, platforms: List[Platform]) -> None:
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
        _probe_hits_platform(fighter, grounded_probe, platform)
        for platform in platforms
    )

    fighter.near_ground = any(
        _probe_hits_platform(fighter, near_ground_probe, platform)
        for platform in platforms
    )


def _probe_hits_platform(fighter: Fighter, probe: pygame.Rect, platform: Platform) -> bool:
    if platform.is_soft and fighter.drop_through_timer > 0.0:
        return False
    return probe.colliderect(platform.rect)


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
    best_top = None
    foot_x1 = fighter.left + 2
    foot_x2 = fighter.right - 2

    for platform in platforms:
        if platform.is_soft and fighter.drop_through_timer > 0.0:
            continue

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


def is_standing_on_soft_platform(fighter: Fighter, platforms: List[Platform]) -> bool:
    probe = pygame.Rect(
        int(fighter.rect_x) + 2,
        int(fighter.bottom),
        max(1, fighter.width - 4),
        4,
    )

    for platform in platforms:
        if not platform.is_soft:
            continue
        if probe.colliderect(platform.rect):
            return True

    return False
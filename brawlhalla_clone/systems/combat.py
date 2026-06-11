# systems/combat.py

import pygame

from core.player import Player
from core.dummy import Dummy


def tick_combat_timers(player: Player, dummy: Dummy, dt: float) -> None:
    if player.attack_timer > 0.0:
        player.attack_timer = max(0.0, player.attack_timer - dt)

    if player.ultimate_timer > 0.0:
        player.ultimate_timer = max(0.0, player.ultimate_timer - dt)

    if dummy.hitstun_timer > 0.0:
        dummy.hitstun_timer = max(0.0, dummy.hitstun_timer - dt)


def try_start_attack(player: Player) -> None:
    if player.is_attacking:
        return
    if player.landing_recovery_timer > 0.0:
        return

    move_x = player.input.move_x
    up_or_down = player.input.up or player.input.down

    if up_or_down:
        _start_attack(player, "kick", 0.40)
    elif move_x != 0:
        _start_attack(player, "punch", 0.16)
    else:
        _start_attack(player, "uppercut", 0.40)


def try_start_ultimate(player: Player) -> None:
    if not player.ultimate_ready:
        return

    player.ultimate_timer = 5.0
    player.ultimate_ready = False


def _start_attack(player: Player, name: str, total_time: float) -> None:
    player.is_attacking = True
    player.attack_name = name
    player.attack_timer = total_time
    player.attack_total_time = total_time
    player.attack_has_hit = False


def update_attack(player: Player, dummy: Dummy, dt: float) -> None:
    if not player.is_attacking:
        return

    # 발차기 중 전진
    if player.attack_name == "kick":
        player.vel.x = player.facing * 500.0

    active = _is_attack_active(player)
    if active and not player.attack_has_hit:
        hitbox = get_attack_hitbox(player)
        dummy_rect = pygame.Rect(
            int(dummy.rect_x),
            int(dummy.rect_y),
            dummy.width,
            dummy.height,
        )
        if hitbox is not None and hitbox.colliderect(dummy_rect):
            _apply_hit(player, dummy)
            player.attack_has_hit = True

    if player.attack_timer <= 0.0:
        player.is_attacking = False
        player.attack_name = None
        player.attack_total_time = 0.0
        player.attack_has_hit = False


def _is_attack_active(player: Player) -> bool:
    if player.attack_name is None:
        return False

    elapsed = player.attack_total_time - player.attack_timer

    if player.attack_name == "uppercut":
        return 0.10 <= elapsed <= 0.20
    if player.attack_name == "punch":
        return 0.03 <= elapsed <= 0.10
    if player.attack_name == "kick":
        return 0.08 <= elapsed <= 0.32

    return False


def get_attack_hitbox(player: Player) -> pygame.Rect | None:
    if player.attack_name is None:
        return None
    if not _is_attack_active(player):
        return None

    bonus = 55 if player.ultimate_timer > 0.0 else 0

    if player.attack_name == "uppercut":
        w = 70 + bonus
        h = 90
        x = player.pos.x + player.facing * 30 - (w / 2)
        y = player.pos.y - 75
        return pygame.Rect(int(x), int(y), int(w), int(h))

    if player.attack_name == "punch":
        w = 55 + bonus
        h = 36
        x = player.pos.x + player.facing * 35 - (w / 2)
        y = player.pos.y - 10
        return pygame.Rect(int(x), int(y), int(w), int(h))

    if player.attack_name == "kick":
        w = 90 + bonus
        h = 46
        x = player.pos.x + player.facing * 38 - (w / 2)
        y = player.pos.y - 6
        return pygame.Rect(int(x), int(y), int(w), int(h))

    return None


def _apply_hit(player: Player, dummy: Dummy) -> None:
    name = player.attack_name

    if name == "uppercut":
        dummy.vel.x = player.facing * 380.0
        dummy.vel.y = -760.0
        dummy.hitstun_timer = 0.30
    elif name == "punch":
        dummy.vel.x = player.facing * 180.0
        dummy.vel.y = -120.0
        dummy.hitstun_timer = 0.10
    elif name == "kick":
        dummy.vel.x = player.facing * 520.0
        dummy.vel.y = -420.0
        dummy.hitstun_timer = 0.25


def update_dummy(dummy: Dummy, dt: float, ground_y: float) -> None:
    gravity = 2200.0

    if dummy.bottom < ground_y or dummy.vel.y < 0:
        dummy.vel.y += gravity * dt

    dummy.pos.x += dummy.vel.x * dt
    dummy.pos.y += dummy.vel.y * dt

    # 단순 마찰
    dummy.vel.x *= 0.92

    # 바닥 충돌
    if dummy.bottom >= ground_y:
        dummy.pos.y = ground_y - dummy.height / 2
        if dummy.vel.y > 0:
            dummy.vel.y = 0.0
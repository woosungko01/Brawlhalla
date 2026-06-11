# systems/combat.py

import pygame

from core.player import Player
from core.dummy import Dummy


def tick_combat_timers(player: Player, dummy: Dummy, dt: float) -> None:
    if player.attack_timer > 0.0:
        player.attack_timer = max(0.0, player.attack_timer - dt)

    if player.ultimate_timer > 0.0:
        player.ultimate_timer = max(0.0, player.ultimate_timer - dt)

    if player.stun_timer > 0.0:
        player.stun_timer = max(0.0, player.stun_timer - dt)

    if player.attack_tick_timer > 0.0:
        player.attack_tick_timer = max(0.0, player.attack_tick_timer - dt)

    if dummy.hitstun_timer > 0.0:
        dummy.hitstun_timer = max(0.0, dummy.hitstun_timer - dt)


def try_start_attack(player: Player) -> None:
    if player.is_attacking:
        return
    if player.landing_recovery_timer > 0.0:
        return
    if player.stun_timer > 0.0:
        return

    attack_name = resolve_basic_attack(player)
    if attack_name is None:
        return

    total = get_attack_total_time(attack_name)
    _start_attack(player, attack_name, total)


def try_start_ultimate(player: Player) -> None:
    if player.is_attacking:
        return
    if player.stun_timer > 0.0:
        return
    if not player.ultimate_ready:
        return

    if player.character_id == "brawler":
        player.ultimate_timer = 5.0

    elif player.character_id == "swordsman":
        _start_attack(player, "sword_ultimate", 1.20)

    elif player.character_id == "gunner":
        _start_attack(player, "gunner_ultimate", 4.0)
        player.attack_tick_timer = 0.0


def resolve_basic_attack(player: Player) -> str | None:
    if player.character_id == "brawler":
        if player.input.up or player.input.down:
            return "brawler_kick"
        elif player.input.move_x != 0:
            return "brawler_punch"
        else:
            return "brawler_uppercut"

    if player.character_id == "swordsman":
        if player.input.up:
            return "sword_up_slash"
        elif player.input.down:
            return "sword_down_slash"
        elif player.input.move_x != 0:
            return "sword_side_slash"
        else:
            return "sword_counter"

    if player.character_id == "gunner":
        if player.input.up:
            return "gunner_up_shot"
        elif player.input.down:
            return "gunner_down_shot"
        elif player.input.move_x != 0:
            return "gunner_side_shot"
        else:
            return "gunner_low_shot"

    return None


def get_attack_total_time(name: str) -> float:
    table = {
        "brawler_uppercut": 0.40,
        "brawler_punch": 0.16,
        "brawler_kick": 0.40,

        "sword_counter": 0.30,
        "sword_side_slash": 0.30,
        "sword_up_slash": 0.36,
        "sword_down_slash": 0.36,
        "sword_ultimate": 1.20,

        "gunner_low_shot": 0.14,
        "gunner_side_shot": 0.12,
        "gunner_up_shot": 0.14,
        "gunner_down_shot": 0.14,
        "gunner_ultimate": 4.0,
    }
    return table[name]


def _start_attack(player: Player, name: str, total_time: float) -> None:
    player.is_attacking = True
    player.attack_name = name
    player.attack_timer = total_time
    player.attack_total_time = total_time
    player.attack_has_hit = False
    player.attack_extra_fired = False
    player.attack_tick_timer = 0.0


def update_attack(player: Player, dummy: Dummy, dt: float) -> None:
    if not player.is_attacking or player.attack_name is None:
        return

    name = player.attack_name

    if name == "brawler_kick":
        player.vel.x = player.facing * 500.0

    elif name in (
        "brawler_uppercut",
        "sword_counter",
        "sword_side_slash",
        "sword_up_slash",
        "sword_down_slash",
        "sword_ultimate",
    ):
        player.vel.x = 0.0

    elif name in (
        "gunner_low_shot",
        "gunner_side_shot",
        "gunner_up_shot",
        "gunner_down_shot",
    ):
        player.vel.x = 0.0

    elif name == "gunner_ultimate":
        # 이동 가능하게 처리
        move_x = player.input.move_x
        player.vel.x = move_x * player.move_cfg.MAX_RUN_SPEED

        if player.attack_tick_timer <= 0.0:
            hitbox = get_attack_hitbox(player)
            if hitbox is not None:
                _try_hit_dummy(player, dummy, hitbox)
            player.attack_tick_timer = 0.12

    if name == "sword_ultimate":
        elapsed = player.attack_total_time - player.attack_timer

        if elapsed < 1.0:
            player.vel.x = 0.0
            player.vel.y = 0.0
        elif not player.attack_extra_fired:
            hitbox = get_attack_hitbox(player)
            if hitbox is not None:
                _try_hit_dummy(player, dummy, hitbox)
            player.attack_extra_fired = True

    elif name != "gunner_ultimate":
        active = _is_attack_active(player)
        if active and not player.attack_has_hit:
            hitbox = get_attack_hitbox(player)
            if hitbox is not None:
                _try_hit_dummy(player, dummy, hitbox)

    if player.attack_timer <= 0.0:
        player.is_attacking = False
        player.attack_name = None
        player.attack_total_time = 0.0
        player.attack_has_hit = False
        player.attack_extra_fired = False
        player.attack_tick_timer = 0.0


def _is_attack_active(player: Player) -> bool:
    if player.attack_name is None:
        return False

    elapsed = player.attack_total_time - player.attack_timer
    name = player.attack_name

    windows = {
        "brawler_uppercut": (0.10, 0.20),
        "brawler_punch": (0.03, 0.10),
        "brawler_kick": (0.08, 0.32),

        "sword_counter": (0.05, 0.20),
        "sword_side_slash": (0.12, 0.20),
        "sword_up_slash": (0.14, 0.24),
        "sword_down_slash": (0.14, 0.24),

        "gunner_low_shot": (0.03, 0.08),
        "gunner_side_shot": (0.02, 0.06),
        "gunner_up_shot": (0.03, 0.08),
        "gunner_down_shot": (0.03, 0.08),
    }

    if name not in windows:
        return False

    start, end = windows[name]
    return start <= elapsed <= end


def get_attack_hitbox(player: Player) -> pygame.Rect | None:
    if player.attack_name is None:
        return None

    bonus = 55 if player.ultimate_timer > 0.0 else 0
    name = player.attack_name

    if name not in ("sword_ultimate", "gunner_ultimate") and not _is_attack_active(player):
        return None

    if name == "brawler_uppercut":
        w = 70 + bonus
        h = 90
        x = player.pos.x + player.facing * 30 - (w / 2)
        y = player.pos.y - 75
        return pygame.Rect(int(x), int(y), int(w), int(h))

    if name == "brawler_punch":
        w = 55 + bonus
        h = 36
        x = player.pos.x + player.facing * 35 - (w / 2)
        y = player.pos.y - 10
        return pygame.Rect(int(x), int(y), int(w), int(h))

    if name == "brawler_kick":
        w = 90 + bonus
        h = 46
        x = player.pos.x + player.facing * 38 - (w / 2)
        y = player.pos.y - 6
        return pygame.Rect(int(x), int(y), int(w), int(h))

    if name == "sword_counter":
        w = 42
        h = 72
        x = player.pos.x + player.facing * 28 - (w / 2)
        y = player.pos.y - 36
        return pygame.Rect(int(x), int(y), int(w), int(h))

    if name == "sword_side_slash":
        w = 105 + bonus
        h = 42
        x = player.pos.x + player.facing * 58 - (w / 2)
        y = player.pos.y - 14
        return pygame.Rect(int(x), int(y), int(w), int(h))

    if name == "sword_up_slash":
        w = 105 + bonus
        h = 70
        x = player.pos.x + player.facing * 38 - (w / 2)
        y = player.pos.y - 88
        return pygame.Rect(int(x), int(y), int(w), int(h))

    if name == "sword_down_slash":
        w = 105 + bonus
        h = 70
        x = player.pos.x + player.facing * 38 - (w / 2)
        y = player.pos.y + 8
        return pygame.Rect(int(x), int(y), int(w), int(h))

    if name == "sword_ultimate":
        elapsed = player.attack_total_time - player.attack_timer
        if not (1.00 <= elapsed <= 1.12):
            return None

        w = 500
        h = 160
        y = player.pos.y - 80

        if player.facing == 1:
            x = player.pos.x + 10
        else:
            x = player.pos.x - 10 - w

        return pygame.Rect(int(x), int(y), int(w), int(h))

    if name == "gunner_low_shot":
        # 전방 아래 하체 사격 - 길이 축소
        w = 80
        h = 26
        if player.facing == 1:
            x = player.pos.x + 18
        else:
            x = player.pos.x - 18 - w
        y = player.pos.y + 18
        return pygame.Rect(int(x), int(y), int(w), int(h))

    if name == "gunner_side_shot":
        # 히트스캔 느낌 - 길이 절반 수준으로 축소
        w = 140
        h = 18
        if player.facing == 1:
            x = player.pos.x + 18
        else:
            x = player.pos.x - 18 - w
        y = player.pos.y - 12
        return pygame.Rect(int(x), int(y), int(w), int(h))

    if name == "gunner_up_shot":
        # 머리 위 넓게
        w = 120
        h = 60
        x = player.pos.x - (w / 2)
        y = player.pos.y - 110
        return pygame.Rect(int(x), int(y), int(w), int(h))

    if name == "gunner_down_shot":
        # 발밑 넓게
        w = 120
        h = 60
        x = player.pos.x - (w / 2)
        y = player.pos.y + 20
        return pygame.Rect(int(x), int(y), int(w), int(h))

    if name == "gunner_ultimate":
        # 원형 느낌 더 크게
        w = 320
        h = 320
        x = player.pos.x - (w / 2)
        y = player.pos.y - (h / 2)
        return pygame.Rect(int(x), int(y), int(w), int(h))

    return None


def _try_hit_dummy(player: Player, dummy: Dummy, hitbox: pygame.Rect) -> None:
    dummy_rect = pygame.Rect(
        int(dummy.rect_x),
        int(dummy.rect_y),
        dummy.width,
        dummy.height,
    )

    if hitbox.colliderect(dummy_rect):
        _apply_hit(player, dummy)
        player.attack_has_hit = True


def _apply_hit(player: Player, dummy: Dummy) -> None:
    name = player.attack_name

    if name == "brawler_uppercut":
        dummy.vel.x = player.facing * 380.0
        dummy.vel.y = -760.0
        dummy.hitstun_timer = 0.30

    elif name == "brawler_punch":
        dummy.vel.x = player.facing * 180.0
        dummy.vel.y = -120.0
        dummy.hitstun_timer = 0.10

    elif name == "brawler_kick":
        dummy.vel.x = player.facing * 520.0
        dummy.vel.y = -420.0
        dummy.hitstun_timer = 0.25

    elif name == "sword_side_slash":
        dummy.vel.x = player.facing * 340.0
        dummy.vel.y = -180.0
        dummy.hitstun_timer = 0.18

    elif name == "sword_up_slash":
        dummy.vel.x = player.facing * 120.0
        dummy.vel.y = -900.0
        dummy.hitstun_timer = 0.28

    elif name == "sword_down_slash":
        dummy.vel.x = player.facing * 150.0
        dummy.vel.y = 920.0
        dummy.hitstun_timer = 0.28

    elif name == "sword_counter":
        dummy.vel.x = 0.0
        dummy.vel.y = 0.0
        dummy.hitstun_timer = 0.50

    elif name == "sword_ultimate":
        dummy.vel.x = player.facing * 900.0
        dummy.vel.y = -720.0
        dummy.hitstun_timer = 0.55

    elif name == "gunner_low_shot":
        dummy.vel.x = player.facing * 220.0
        dummy.vel.y = 80.0
        dummy.hitstun_timer = 0.10

    elif name == "gunner_side_shot":
        dummy.vel.x = player.facing * 420.0
        dummy.vel.y = -50.0
        dummy.hitstun_timer = 0.12

    elif name == "gunner_up_shot":
        dummy.vel.x = 0.0
        dummy.vel.y = -820.0
        dummy.hitstun_timer = 0.16

    elif name == "gunner_down_shot":
        dummy.vel.x = 0.0
        dummy.vel.y = 900.0
        dummy.hitstun_timer = 0.16

    elif name == "gunner_ultimate":
        dx = dummy.pos.x - player.pos.x
        if dx == 0:
            dx = 1.0
        direction = 1 if dx > 0 else -1
        dummy.vel.x = direction * 420.0
        dummy.vel.y = -240.0
        dummy.hitstun_timer = 0.14


def update_dummy(dummy: Dummy, dt: float, ground_y: float) -> None:
    gravity = 2200.0

    if dummy.bottom < ground_y or dummy.vel.y < 0:
        dummy.vel.y += gravity * dt

    dummy.pos.x += dummy.vel.x * dt
    dummy.pos.y += dummy.vel.y * dt

    dummy.vel.x *= 0.92

    if dummy.bottom >= ground_y:
        dummy.pos.y = ground_y - dummy.height / 2
        if dummy.vel.y > 0:
            dummy.vel.y = 0.0
# main.py

import sys
import pygame

from core.player import Player
from core.input_state import InputState
from core.camera import Camera
from core.dummy import Dummy

from systems.movement import apply_horizontal_control
from systems.jump import try_request_jump, execute_pending_jump
from systems.gravity import apply_vertical_forces
from systems.dash import (
    tick_dash_timers,
    try_request_dash,
    update_dash,
)
from systems.collision import (
    Platform,
    move_and_collide,
    update_grounded,
    handle_landing,
    snap_to_ground,
)
from systems.state_machine import update_move_state
from systems.combat import (
    tick_combat_timers,
    try_start_attack,
    try_start_ultimate,
    update_attack,
    get_attack_hitbox,
    update_dummy,
)

from utils.debug_hud import draw_debug_hud


SCREEN_W, SCREEN_H = 1280, 720
WORLD_W, WORLD_H = 3200, 1800

FPS = 60
TITLE = "Brawlhalla 이동 + 2캐릭터 공격 프로토타입"

BG_COLOR = (30, 30, 45)
PLAYER_COLOR = (100, 180, 255)
PLATFORM_COLOR = (80, 200, 120)
WORLD_BORDER_COLOR = (90, 90, 120)
DUMMY_COLOR = (230, 120, 120)
HITBOX_COLOR = (255, 220, 80)


def build_platforms() -> list[Platform]:
    return [
        Platform(0, 1760, 3200, 40),
        Platform(150, 1500, 250, 20),
        Platform(450, 1380, 220, 20),
        Platform(120, 1220, 180, 20),
        Platform(700, 1450, 300, 20),
        Platform(1100, 1300, 260, 20),
        Platform(900, 1120, 220, 20),
        Platform(1400, 980, 250, 20),
        Platform(1900, 1500, 280, 20),
        Platform(2300, 1360, 240, 20),
        Platform(2600, 1200, 220, 20),
        Platform(2900, 1020, 180, 20),
        Platform(1650, 1600, 180, 20),
        Platform(2100, 1180, 160, 20),
        Platform(2500, 900, 150, 20),
    ]


def tick_timers(player: Player, dt: float) -> None:
    if player.jump_startup_timer > 0.0:
        player.jump_startup_timer = max(0.0, player.jump_startup_timer - dt)

    if player.landing_recovery_timer > 0.0:
        player.landing_recovery_timer = max(0.0, player.landing_recovery_timer - dt)

    if player.fast_fall_lock_timer > 0.0:
        player.fast_fall_lock_timer = max(0.0, player.fast_fall_lock_timer - dt)

    if player.dodge_cooldown_timer > 0.0:
        player.dodge_cooldown_timer = max(0.0, player.dodge_cooldown_timer - dt)


def read_input(inp: InputState, events: list[pygame.event.Event]) -> None:
    inp.reset_frame_events()
    keys = pygame.key.get_pressed()

    inp.left = keys[pygame.K_a] or keys[pygame.K_LEFT]
    inp.right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
    inp.down = keys[pygame.K_s] or keys[pygame.K_DOWN]
    inp.up = keys[pygame.K_w] or keys[pygame.K_UP]

    inp.jump = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
    inp.dodge = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
    inp.attack = keys[pygame.K_j]
    inp.ultimate = keys[pygame.K_k]

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                inp.jump_pressed = True
            if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                inp.dodge_pressed = True
            if event.key == pygame.K_j:
                inp.attack_pressed = True
            if event.key == pygame.K_k:
                inp.ultimate_pressed = True

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                inp.jump_released = True


def update_player(player: Player, dummy: Dummy, dt: float, platforms: list[Platform]) -> None:
    player.was_grounded = player.is_grounded

    if not player.is_grounded:
        player.left_ground_since_dash = True

    tick_timers(player, dt)
    tick_dash_timers(player, dt)
    tick_combat_timers(player, dummy, dt)

    if player.input.ultimate_pressed:
        try_start_ultimate(player)

    if player.input.attack_pressed:
        try_start_attack(player)

    if player.input.dodge_pressed and not player.is_attacking and player.stun_timer <= 0.0:
        if not player.is_grounded and player.near_ground:
            snap_to_ground(player, platforms)
        try_request_dash(player)

    if player.input.jump_pressed and not player.is_attacking and player.stun_timer <= 0.0:
        try_request_jump(player)

    execute_pending_jump(player)

    if player.is_attacking:
        update_attack(player, dummy, dt)
    elif player.is_dashing:
        update_dash(player, dt)
    else:
        apply_horizontal_control(player, dt)

    apply_vertical_forces(player, dt)
    move_and_collide(player, dt, platforms)
    update_grounded(player, platforms)
    handle_landing(player)
    update_move_state(player)


def draw(
    surface: pygame.Surface,
    player: Player,
    dummy: Dummy,
    platforms: list[Platform],
    camera: Camera,
    show_hud: bool,
    font: pygame.font.Font,
) -> None:
    surface.fill(BG_COLOR)

    world_rect = pygame.Rect(
        int(-camera.x),
        int(-camera.y),
        WORLD_W,
        WORLD_H,
    )
    pygame.draw.rect(surface, WORLD_BORDER_COLOR, world_rect, 3)

    for plat in platforms:
        rect = pygame.Rect(
            int(plat.x - camera.x),
            int(plat.y - camera.y),
            int(plat.width),
            int(plat.height),
        )
        pygame.draw.rect(surface, PLATFORM_COLOR, rect)
        pygame.draw.rect(surface, (60, 160, 90), rect, 2)

    # 더미
    drect = pygame.Rect(
        int(dummy.rect_x - camera.x),
        int(dummy.rect_y - camera.y),
        dummy.width,
        dummy.height,
    )
    pygame.draw.rect(surface, DUMMY_COLOR, drect)
    pygame.draw.rect(surface, (180, 80, 80), drect, 2)

    # 플레이어
    prect = pygame.Rect(
        int(player.rect_x - camera.x),
        int(player.rect_y - camera.y),
        player.width,
        player.height,
    )
    pygame.draw.rect(surface, PLAYER_COLOR, prect)
    pygame.draw.rect(surface, (60, 140, 220), prect, 2)

    eye_x = int(player.pos.x - camera.x + player.facing * 10)
    eye_y = int(player.rect_y - camera.y + 14)
    pygame.draw.circle(surface, (255, 255, 255), (eye_x, eye_y), 5)

    state_surf = font.render(player.move_state, True, (200, 200, 200))
    surface.blit(
        state_surf,
        (
            int(player.pos.x - camera.x - state_surf.get_width() // 2),
            int(player.rect_y - camera.y - 22),
        ),
    )

    char_surf = font.render(player.character_id, True, (255, 255, 255))
    surface.blit(char_surf, (20, 20))

    attack_hitbox = get_attack_hitbox(player)
    if attack_hitbox is not None:
        hb = pygame.Rect(
            int(attack_hitbox.x - camera.x),
            int(attack_hitbox.y - camera.y),
            attack_hitbox.width,
            attack_hitbox.height,
        )
        pygame.draw.rect(surface, HITBOX_COLOR, hb, 2)

    if player.ultimate_timer > 0.0:
        ult_surf = font.render("ULT ACTIVE", True, (255, 220, 120))
        surface.blit(ult_surf, (20, 60))

    if show_hud:
        draw_debug_hud(surface, player)

    pygame.display.flip()


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 13)

    player = Player()
    player.input = InputState()
    player.pos.x = 300.0
    player.pos.y = 1400.0
    player.character_id = "brawler"

    platforms = build_platforms()
    dummy = Dummy(WORLD_W / 2, 1760 - 40 - 36)

    camera = Camera(SCREEN_W, SCREEN_H, WORLD_W, WORLD_H)
    camera.update(player.pos.x, player.pos.y)

    show_hud = True

    while True:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    show_hud = not show_hud

                if event.key == pygame.K_r:
                    player = Player()
                    player.input = InputState()
                    player.pos.x = 300.0
                    player.pos.y = 1400.0
                    player.character_id = "brawler"
                    dummy = Dummy(WORLD_W / 2, 1760 - 40 - 36)

                # 캐릭터 전환 테스트
                if event.key == pygame.K_1:
                    player.character_id = "brawler"
                if event.key == pygame.K_2:
                    player.character_id = "swordsman"

        read_input(player.input, events)
        update_player(player, dummy, dt, platforms)
        update_dummy(dummy, dt, 1760.0)

        camera.update(player.pos.x, player.pos.y)
        draw(screen, player, dummy, platforms, camera, show_hud, font)


if __name__ == "__main__":
    main()
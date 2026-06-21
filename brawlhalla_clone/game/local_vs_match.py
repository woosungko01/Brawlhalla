from __future__ import annotations

import pygame

from core.camera import Camera
from core.input_state import InputState

from stages.test_stage import build_test_stage

from entities.player_fighter import PlayerFighter

from characters.brawler import BrawlerCharacter
from characters.swordsman import SwordsmanCharacter
from characters.gunner import GunnerCharacter

from effects.trail_effect import TrailEffect

from systems.movement import apply_horizontal_control
from systems.jump import try_request_jump, execute_pending_jump
from systems.gravity import apply_vertical_forces
from systems.dash import tick_dash_timers, try_request_dash, update_dash
from systems.collision import (
    move_and_collide,
    update_grounded,
    handle_landing,
    snap_to_ground,
    update_wall_cling,
    handle_wall_touch,
    handle_wall_detach_inputs,
    is_standing_on_soft_platform,
)
from systems.state_machine import update_move_state
from systems.fighter_combat import (
    tick_combat_timers,
    try_start_attack,
    try_start_ultimate,
    update_attack,
    apply_pending_launch_if_ready,
)
from systems.dodge import (
    tick_dodge_timers,
    try_request_dodge,
    update_dodge,
    cancel_dodge,
)
from rendering.match_renderer import MatchRenderer


class LocalVsMatch:
    #2인 pvp 게임 구조
    def __init__(self, screen_w: int, screen_h: int, p1_char: str, p2_char: str) -> None:
        self.stage = build_test_stage()
        self.camera = Camera(screen_w, screen_h, self.stage.world_w, self.stage.world_h)
        self.show_hud = True
        self.show_hitboxes = True
        self.show_fighter_labels = True
        self.minimal_ui = False
        self.opening_text = None
        self.allow_debug_toggle = True

        self.renderer = MatchRenderer()

        self.characters = {
            "brawler": BrawlerCharacter(),
            "swordsman": SwordsmanCharacter(),
            "gunner": GunnerCharacter(),
        }

        self.player1 = PlayerFighter(
            self.stage.player_spawn_x,
            self.stage.player_spawn_y,
            self.characters[p1_char],
        )
        self.player1.player_index = 1
        self.player1.input = InputState()
        self.player1.spawn_x = self.stage.player_spawn_x
        self.player1.spawn_y = self.stage.player_spawn_y

        self.player2 = PlayerFighter(
            self.stage.dummy_spawn_x,
            self.stage.dummy_spawn_y,
            self.characters[p2_char],
        )
        self.player2.player_index = 2
        self.player2.input = InputState()
        self.player2.spawn_x = self.stage.dummy_spawn_x
        self.player2.spawn_y = self.stage.dummy_spawn_y
        self.player2.facing = -1

        self.winner: PlayerFighter | None = None
        self.is_match_over = False

        self.ko_left_x = 60
        self.ko_right_x = self.stage.world_w - 60
        self.ko_top_y = 0
        self.ko_bottom_y = self.stage.world_h

        self.ko_banner_text: str | None = None
        self.ko_banner_timer = 0.0

        self.camera_shake_timer = 0.0
        self.camera_shake_strength = 0.0

        update_grounded(self.player1, self.stage.platforms)
        update_grounded(self.player2, self.stage.platforms)

    def tick_timers(self, fighter, dt: float) -> None:
        if fighter.jump_startup_timer > 0.0:
            fighter.jump_startup_timer = max(0.0, fighter.jump_startup_timer - dt)

        if fighter.fast_fall_lock_timer > 0.0:
            fighter.fast_fall_lock_timer = max(0.0, fighter.fast_fall_lock_timer - dt)

        if fighter.dodge_cooldown_timer > 0.0:
            fighter.dodge_cooldown_timer = max(0.0, fighter.dodge_cooldown_timer - dt)

        if fighter.wall_detach_grace_timer > 0.0:
            fighter.wall_detach_grace_timer = max(0.0, fighter.wall_detach_grace_timer - dt)

        if fighter.drop_through_timer > 0.0:
            fighter.drop_through_timer = max(0.0, fighter.drop_through_timer - dt)

        if fighter.invuln_timer > 0.0:
            fighter.invuln_timer = max(0.0, fighter.invuln_timer - dt)

    def update_trail_effects(self, fighter, dt: float) -> None:
        alive: list[TrailEffect] = []
        for fx in fighter.trail_effects:
            fx.lifetime -= dt
            if fx.lifetime > 0.0:
                alive.append(fx)
        fighter.trail_effects = alive

        if fighter.hitstun_timer <= 0.0:
            fighter.trail_spawn_timer = 0.0
            return

        speed_sq = fighter.vel.x * fighter.vel.x + fighter.vel.y * fighter.vel.y
        if speed_sq < 180.0 * 180.0:
            fighter.trail_spawn_timer = 0.0
            return

        fighter.trail_spawn_timer -= dt
        if fighter.trail_spawn_timer > 0.0:
            return

        fighter.trail_effects.append(
            TrailEffect(
                x=fighter.pos.x,
                y=fighter.pos.y,
                lifetime=0.30,
                max_lifetime=0.30,
                scale=0.60,
            )
        )

        fighter.trail_spawn_timer = 0.035

    def update_fighter(self, fighter, targets: list, dt: float) -> None:
        fighter.was_grounded = fighter.is_grounded

        if not fighter.is_grounded:
            fighter.left_ground_since_dash = True

        self.tick_timers(fighter, dt)
        tick_dash_timers(fighter, dt)
        tick_combat_timers(fighter, dt)
        tick_dodge_timers(fighter, dt)

        apply_pending_launch_if_ready(fighter)

        if fighter.hit_freeze_timer > 0.0:
            fighter.vel.x = 0.0
            fighter.vel.y = 0.0
            self.update_trail_effects(fighter, dt)
            update_move_state(fighter)
            return

        if fighter.input.ultimate_pressed:
            try_start_ultimate(fighter)

        if fighter.input.attack_pressed:
            if fighter.is_dodging:
                cancel_dodge(fighter)
            try_start_attack(fighter)

        if (
            fighter.is_grounded
            and fighter.input.down
            and fighter.drop_through_timer <= 0.0
            and not fighter.is_dodging
            and not fighter.is_dashing
            and is_standing_on_soft_platform(fighter, self.stage.platforms)
        ):
            fighter.drop_through_timer = 0.18
            fighter.is_grounded = False
            if fighter.vel.y < 60.0:
                fighter.vel.y = 60.0

        if fighter.input.dodge_pressed and fighter.stun_timer <= 0.0 and fighter.hitstun_timer <= 0.0:
            dodge_started = try_request_dodge(fighter)

            if not dodge_started and not fighter.is_attacking:
                if (
                    not fighter.is_grounded
                    and fighter.input.down
                    and fighter.fast_fall_lock_timer <= 0.0
                    and fighter.vel.y >= 0.0
                    and fighter.near_ground
                ):
                    snap_to_ground(fighter, self.stage.platforms)

                try_request_dash(fighter)

        if fighter.input.jump_pressed and not fighter.is_attacking and fighter.stun_timer <= 0.0 and fighter.hitstun_timer <= 0.0:
            try_request_jump(fighter)

        execute_pending_jump(fighter)

        if fighter.is_attacking:
            update_attack(fighter, targets, dt)
        elif fighter.is_dodging:
            update_dodge(fighter, dt)
        elif fighter.is_dashing:
            update_dash(fighter, dt)
        else:
            if fighter.hitstun_timer <= 0.0 and fighter.stun_timer <= 0.0:
                apply_horizontal_control(fighter, dt)

        apply_vertical_forces(fighter, dt)
        move_and_collide(fighter, dt, self.stage.platforms)
        update_grounded(fighter, self.stage.platforms)

        update_wall_cling(fighter)
        handle_wall_detach_inputs(fighter)
        handle_wall_touch(fighter)

        handle_landing(fighter)
        update_move_state(fighter)
        self.update_trail_effects(fighter, dt)

    def find_respawn_point(self, fallen_x: float, fighter_height: int) -> tuple[float, float]:
        best_platform = None
        best_dist = None

        for platform in self.stage.platforms:
            center_x = platform.x + platform.width * 0.5
            dist = abs(center_x - fallen_x)

            if best_dist is None or dist < best_dist:
                best_dist = dist
                best_platform = platform

        if best_platform is None:
            return self.stage.player_spawn_x, self.stage.player_spawn_y

        px = best_platform.x + best_platform.width * 0.5
        py = best_platform.y - (fighter_height * 0.5) - 8
        return px, py

    def handle_ko(self, fighter: PlayerFighter) -> None:
        if fighter.is_ko or fighter.is_dead:
            return

        fighter.is_ko = True
        fighter.stocks -= 1

        self.ko_banner_text = f"P{fighter.player_index} KNOCKOUT!"
        self.ko_banner_timer = 1.2

        self.camera_shake_timer = 0.45
        self.camera_shake_strength = 18.0

        if fighter.stocks <= 0:
            fighter.is_dead = True
            self.is_match_over = True
            self.winner = self.player1 if fighter is self.player2 else self.player2
            return

        respawn_x, respawn_y = self.find_respawn_point(fighter.pos.x, fighter.height)
        fighter.respawn_at(respawn_x, respawn_y, invuln_time=3.0)

        other = self.player1 if fighter is self.player2 else self.player2
        other.invuln_timer = max(other.invuln_timer, 3.0)

    def check_ko(self) -> None:
        if self.player1.pos.x < self.ko_left_x:
            self.handle_ko(self.player1)
        if self.player1.pos.x > self.ko_right_x:
            self.handle_ko(self.player1)
        if self.player1.pos.y < self.ko_top_y:
            self.handle_ko(self.player1)
        if self.player1.pos.y > self.ko_bottom_y:
            self.handle_ko(self.player1)

        if self.player2.pos.x < self.ko_left_x:
            self.handle_ko(self.player2)
        if self.player2.pos.x > self.ko_right_x:
            self.handle_ko(self.player2)
        if self.player2.pos.y < self.ko_top_y:
            self.handle_ko(self.player2)
        if self.player2.pos.y > self.ko_bottom_y:
            self.handle_ko(self.player2)

    def update(self, dt: float) -> None:
        if self.is_match_over:
            if self.ko_banner_timer > 0.0:
                self.ko_banner_timer = max(0.0, self.ko_banner_timer - dt)
                if self.ko_banner_timer <= 0.0:
                    self.ko_banner_text = None

            if self.camera_shake_timer > 0.0:
                self.camera_shake_timer = max(0.0, self.camera_shake_timer - dt)

            self.camera.set_dual_target(
                self.player1.pos.x, self.player1.pos.y,
                self.player2.pos.x, self.player2.pos.y,
            )
            return

        self.update_fighter(self.player1, [self.player2], dt)
        self.update_fighter(self.player2, [self.player1], dt)

        self.check_ko()

        if self.ko_banner_timer > 0.0:
            self.ko_banner_timer = max(0.0, self.ko_banner_timer - dt)
            if self.ko_banner_timer <= 0.0:
                self.ko_banner_text = None

        if self.camera_shake_timer > 0.0:
            self.camera_shake_timer = max(0.0, self.camera_shake_timer - dt)

        self.camera.set_dual_target(
            self.player1.pos.x, self.player1.pos.y,
            self.player2.pos.x, self.player2.pos.y,
        )

    def draw(self, surface: pygame.Surface, dt: float, font: pygame.font.Font, draw_debug_hud_fn) -> None:
        self.renderer.draw(surface, self, dt, font, draw_debug_hud_fn)
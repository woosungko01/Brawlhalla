# game/training_match.py

import pygame

from core.camera import Camera
from core.input_state import InputState

from stages.test_stage import build_test_stage

from entities.player_fighter import PlayerFighter
from entities.dummy_fighter import DummyFighter

from characters.brawler import BrawlerCharacter
from characters.swordsman import SwordsmanCharacter
from characters.gunner import GunnerCharacter

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
    get_attack_hitbox,
)


class TrainingMatch:
    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.stage = build_test_stage()
        self.camera = Camera(screen_w, screen_h, self.stage.world_w, self.stage.world_h)
        self.show_hud = True

        self.characters = {
            "brawler": BrawlerCharacter(),
            "swordsman": SwordsmanCharacter(),
            "gunner": GunnerCharacter(),
        }

        self.player = PlayerFighter(
            self.stage.player_spawn_x,
            self.stage.player_spawn_y,
            self.characters["brawler"],
        )
        self.player.input = InputState()

        self.dummy = DummyFighter(
            self.stage.dummy_spawn_x,
            self.stage.dummy_spawn_y,
            self.characters["brawler"],
        )

        # 시작 프레임에서 바닥 판정 먼저 맞춤
        update_grounded(self.player, self.stage.platforms)
        update_grounded(self.dummy, self.stage.platforms)

    def reset(self) -> None:
        current_char = self.player.character

        self.player = PlayerFighter(
            self.stage.player_spawn_x,
            self.stage.player_spawn_y,
            current_char,
        )
        self.player.input = InputState()

        self.dummy = DummyFighter(
            self.stage.dummy_spawn_x,
            self.stage.dummy_spawn_y,
            self.characters["brawler"],
        )

        update_grounded(self.player, self.stage.platforms)
        update_grounded(self.dummy, self.stage.platforms)

    def set_player_character(self, key: str) -> None:
        if key in self.characters:
            self.player.character = self.characters[key]

    def tick_timers(self, fighter, dt: float) -> None:
        if fighter.jump_startup_timer > 0.0:
            fighter.jump_startup_timer = max(0.0, fighter.jump_startup_timer - dt)

        if fighter.landing_recovery_timer > 0.0:
            fighter.landing_recovery_timer = max(0.0, fighter.landing_recovery_timer - dt)

        if fighter.fast_fall_lock_timer > 0.0:
            fighter.fast_fall_lock_timer = max(0.0, fighter.fast_fall_lock_timer - dt)

        if fighter.dodge_cooldown_timer > 0.0:
            fighter.dodge_cooldown_timer = max(0.0, fighter.dodge_cooldown_timer - dt)

        if fighter.wall_detach_grace_timer > 0.0:
            fighter.wall_detach_grace_timer = max(0.0, fighter.wall_detach_grace_timer - dt)

        if fighter.drop_through_timer > 0.0:
            fighter.drop_through_timer = max(0.0, fighter.drop_through_timer - dt)

    def update_fighter(self, fighter, targets: list, dt: float) -> None:
        fighter.was_grounded = fighter.is_grounded

        if not fighter.is_grounded:
            fighter.left_ground_since_dash = True

        self.tick_timers(fighter, dt)
        tick_dash_timers(fighter, dt)
        tick_combat_timers(fighter, dt)

        if fighter.input.ultimate_pressed:
            try_start_ultimate(fighter)

        if fighter.input.attack_pressed:
            try_start_attack(fighter)

        # soft platform 위에서 아래 입력 시 drop-through
        if (
            fighter.is_grounded
            and fighter.input.down
            and is_standing_on_soft_platform(fighter, self.stage.platforms)
        ):
            fighter.drop_through_timer = 0.18
            fighter.is_grounded = False
            if fighter.vel.y < 60.0:
                fighter.vel.y = 60.0

        if fighter.input.dodge_pressed and not fighter.is_attacking and fighter.stun_timer <= 0.0:
            # snap dash 조건:
            # - 공중
            # - fast fall 중
            # - 지면 근처
            if (
                    not fighter.is_grounded
                    and fighter.fast_falling
                    and fighter.near_ground
            ):
                snap_to_ground(fighter, self.stage.platforms)

            try_request_dash(fighter)

        if fighter.input.jump_pressed and not fighter.is_attacking and fighter.stun_timer <= 0.0:
            try_request_jump(fighter)

        execute_pending_jump(fighter)

        if fighter.is_attacking:
            update_attack(fighter, targets, dt)
        elif fighter.is_dashing:
            update_dash(fighter, dt)
        else:
            apply_horizontal_control(fighter, dt)

        apply_vertical_forces(fighter, dt)
        move_and_collide(fighter, dt, self.stage.platforms)
        update_grounded(fighter, self.stage.platforms)

        update_wall_cling(fighter)
        handle_wall_detach_inputs(fighter)
        handle_wall_touch(fighter)

        handle_landing(fighter)
        update_move_state(fighter)

    def update_dummy(self, dt: float) -> None:
        """
        훈련용 더미 전용 업데이트.
        - 입력은 받지 않음
        - 피격/낙하/착지만 처리
        """
        d = self.dummy
        d.was_grounded = d.is_grounded

        tick_combat_timers(d, dt)
        self.tick_timers(d, dt)

        # 더미는 스스로 행동하지 않음
        d.input.reset_frame_events()
        d.input.left = False
        d.input.right = False
        d.input.up = False
        d.input.down = False
        d.input.jump = False
        d.input.dodge = False
        d.input.attack = False
        d.input.ultimate = False

        # hitstun 중엔 입력 이동 없음
        if abs(d.vel.x) > 0.0:
            if d.is_grounded:
                d.vel.x *= 0.86
            else:
                d.vel.x *= 0.98

            if abs(d.vel.x) < 5.0:
                d.vel.x = 0.0

        apply_vertical_forces(d, dt)
        move_and_collide(d, dt, self.stage.platforms)
        update_grounded(d, self.stage.platforms)

        update_wall_cling(d)
        handle_wall_touch(d)
        handle_landing(d)
        update_move_state(d)

    def update(self, dt: float) -> None:
        self.update_fighter(self.player, [self.dummy], dt)
        self.update_dummy(dt)
        self.camera.update(self.player.pos.x, self.player.pos.y)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, draw_debug_hud_fn) -> None:
        BG_COLOR = (30, 30, 45)
        PLAYER_COLOR = (100, 180, 255)
        PLATFORM_COLOR = (80, 200, 120)
        WORLD_BORDER_COLOR = (90, 90, 120)
        DUMMY_COLOR = (230, 120, 120)
        HITBOX_COLOR = (255, 220, 80)

        surface.fill(BG_COLOR)

        world_rect = pygame.Rect(
            int(-self.camera.x),
            int(-self.camera.y),
            self.stage.world_w,
            self.stage.world_h,
        )
        pygame.draw.rect(surface, WORLD_BORDER_COLOR, world_rect, 3)

        for plat in self.stage.platforms:
            rect = pygame.Rect(
                int(plat.x - self.camera.x),
                int(plat.y - self.camera.y),
                int(plat.width),
                int(plat.height),
            )
            pygame.draw.rect(surface, PLATFORM_COLOR, rect)
            pygame.draw.rect(surface, (60, 160, 90), rect, 2)

        for fighter, color, border in (
            (self.player, PLAYER_COLOR, (60, 140, 220)),
            (self.dummy, DUMMY_COLOR, (180, 80, 80)),
        ):
            rect = pygame.Rect(
                int(fighter.rect_x - self.camera.x),
                int(fighter.rect_y - self.camera.y),
                fighter.width,
                fighter.height,
            )
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, border, rect, 2)

        eye_x = int(self.player.pos.x - self.camera.x + self.player.facing * 10)
        eye_y = int(self.player.rect_y - self.camera.y + 14)
        pygame.draw.circle(surface, (255, 255, 255), (eye_x, eye_y), 5)

        state_surf = font.render(self.player.move_state, True, (200, 200, 200))
        surface.blit(
            state_surf,
            (
                int(self.player.pos.x - self.camera.x - state_surf.get_width() // 2),
                int(self.player.rect_y - self.camera.y - 22),
            ),
        )

        char_surf = font.render(self.player.character.character_id, True, (255, 255, 255))
        surface.blit(char_surf, (20, 20))

        attack_hitbox = get_attack_hitbox(self.player)
        if attack_hitbox is not None:
            hb = pygame.Rect(
                int(attack_hitbox.x - self.camera.x),
                int(attack_hitbox.y - self.camera.y),
                attack_hitbox.width,
                attack_hitbox.height,
            )
            pygame.draw.rect(surface, HITBOX_COLOR, hb, 2)

        if self.player.ultimate_timer > 0.0:
            ult_surf = font.render("ULT ACTIVE", True, (255, 220, 120))
            surface.blit(ult_surf, (20, 60))

        if self.show_hud:
            draw_debug_hud_fn(surface, self.player)

        pygame.display.flip()
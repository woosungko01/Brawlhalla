import pygame

from core.camera import Camera
from core.input_state import InputState

from stages.test_stage import build_test_stage

from entities.player_fighter import PlayerFighter
from entities.dummy_fighter import DummyFighter

from characters.brawler import BrawlerCharacter
from characters.swordsman import SwordsmanCharacter
from characters.gunner import GunnerCharacter

from combat.followup_buffer import FollowupAction
from effects.trail_effect import TrailEffect

from systems.movement import apply_horizontal_control
from systems.jump import try_request_jump, execute_pending_jump
from systems.gravity import apply_vertical_forces
from systems.collision import (
    move_and_collide,
    update_grounded,
    handle_landing,
    update_wall_cling,
    handle_wall_touch,
    handle_wall_detach_inputs,
    is_standing_on_soft_platform,
    snap_to_ground,
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
from systems.dash import tick_dash_timers, try_request_dash, update_dash
from rendering.match_renderer import MatchRenderer


class TrainingMatch:
    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.stage = build_test_stage()
        self.camera = Camera(screen_w, screen_h, self.stage.world_w, self.stage.world_h)
        self.show_hud = True
        self.renderer = MatchRenderer()

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
        self.dummy.spawn_x = self.stage.dummy_spawn_x
        self.dummy.spawn_y = self.stage.dummy_spawn_y

        self.ko_bottom_y = self.stage.world_h + 220

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
        self.dummy.spawn_x = self.stage.dummy_spawn_x
        self.dummy.spawn_y = self.stage.dummy_spawn_y

        update_grounded(self.player, self.stage.platforms)
        update_grounded(self.dummy, self.stage.platforms)

    def set_player_character(self, key: str) -> None:
        if key in self.characters:
            self.player.character = self.characters[key]

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

    def _store_followup_if_possible(self, fighter, action: FollowupAction) -> None:
        if not fighter.is_attacking:
            return
        if not fighter.can_attack_prestore:
            return
        if fighter.stored_followup_action is not None:
            return

        fighter.stored_followup_action = action

    def _consume_followup_if_ready(self, fighter) -> None:
        if fighter.is_attacking:
            return
        if not fighter.can_attack_prestore:
            return
        if fighter.stored_followup_action is None:
            return
        if fighter.hitstun_timer > 0.0 or fighter.stun_timer > 0.0:
            return
        if fighter.hit_freeze_timer > 0.0:
            return

        action = fighter.stored_followup_action
        fighter.stored_followup_action = None
        fighter.can_attack_prestore = False

        if action.action_type == "dodge":
            original_left = fighter.input.left
            original_right = fighter.input.right
            original_up = fighter.input.up
            original_down = fighter.input.down

            fighter.input.left = action.move_x < 0
            fighter.input.right = action.move_x > 0
            fighter.input.up = action.move_y < 0
            fighter.input.down = action.move_y > 0

            dodge_started = try_request_dodge(fighter)
            if not dodge_started:
                try_request_dash(fighter)

            fighter.input.left = original_left
            fighter.input.right = original_right
            fighter.input.up = original_up
            fighter.input.down = original_down

        elif action.action_type == "attack":
            try_start_attack(fighter)

    def update_fighter(self, fighter, targets: list, dt: float) -> None:
        fighter.was_grounded = fighter.is_grounded

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

        if fighter.stun_timer > 0.0:
            fighter.vel.x = 0.0
            fighter.vel.y = 0.0
            self.update_trail_effects(fighter, dt)
            update_move_state(fighter)
            return

        if fighter.input.ultimate_pressed and fighter.hitstun_timer <= 0.0:
            try_start_ultimate(fighter)

        if fighter.input.attack_pressed:
            self._store_followup_if_possible(
                fighter,
                FollowupAction(action_type="attack"),
            )

            if not fighter.is_attacking and fighter.hitstun_timer <= 0.0:
                if fighter.is_dodging:
                    cancel_dodge(fighter)
                try_start_attack(fighter)

        if (
            fighter.hitstun_timer <= 0.0
            and fighter.is_grounded
            and fighter.input.down
            and fighter.drop_through_timer <= 0.0
            and not fighter.is_dodging
            and is_standing_on_soft_platform(fighter, self.stage.platforms)
        ):
            fighter.drop_through_timer = 0.18
            fighter.is_grounded = False
            if fighter.vel.y < 60.0:
                fighter.vel.y = 60.0

        if fighter.input.dodge_pressed and fighter.stun_timer <= 0.0 and fighter.hitstun_timer <= 0.0:
            self._store_followup_if_possible(
                fighter,
                FollowupAction(
                    action_type="dodge",
                    move_x=fighter.input.move_x,
                    move_y=int(fighter.input.down) - int(fighter.input.up),
                ),
            )

            if not fighter.is_attacking:
                dodge_started = try_request_dodge(fighter)

                if not dodge_started:
                    if (
                        not fighter.is_grounded
                        and fighter.input.down
                        and fighter.fast_fall_lock_timer <= 0.0
                        and fighter.vel.y >= 0.0
                        and fighter.near_ground
                    ):
                        snap_to_ground(fighter, self.stage.platforms)

                    try_request_dash(fighter)

        if (
            fighter.input.jump_pressed
            and not fighter.is_attacking
            and fighter.stun_timer <= 0.0
            and fighter.hitstun_timer <= 0.0
        ):
            try_request_jump(fighter)

        execute_pending_jump(fighter)

        if fighter.hitstun_timer > 0.0:
            pass
        elif fighter.is_attacking:
            update_attack(fighter, targets, dt)
        elif fighter.is_dodging:
            update_dodge(fighter, dt)
        elif fighter.is_dashing:
            update_dash(fighter, dt)
        else:
            apply_horizontal_control(fighter, dt)

        self._consume_followup_if_ready(fighter)

        apply_vertical_forces(fighter, dt)
        move_and_collide(fighter, dt, self.stage.platforms)
        update_grounded(fighter, self.stage.platforms)

        update_wall_cling(fighter)
        handle_wall_detach_inputs(fighter)
        handle_wall_touch(fighter)

        handle_landing(fighter)
        update_move_state(fighter)
        self.update_trail_effects(fighter, dt)

    def respawn_dummy_if_needed(self) -> None:
        if self.dummy.pos.y <= self.ko_bottom_y:
            return

        self.dummy.respawn_at(self.dummy.spawn_x, self.dummy.spawn_y, invuln_time=0.0)
        self.dummy.damage.reset()

    def update_dummy(self, dt: float) -> None:
        d = self.dummy
        d.was_grounded = d.is_grounded

        self.tick_timers(d, dt)
        tick_dash_timers(d, dt)
        tick_combat_timers(d, dt)
        tick_dodge_timers(d, dt)

        apply_pending_launch_if_ready(d)

        if d.hit_freeze_timer > 0.0:
            d.vel.x = 0.0
            d.vel.y = 0.0
            self.update_trail_effects(d, dt)
            update_move_state(d)
            return

        if d.stun_timer > 0.0:
            d.vel.x = 0.0
            d.vel.y = 0.0
            self.update_trail_effects(d, dt)
            update_move_state(d)
            return

        d.input.reset_frame_events()
        d.input.left = False
        d.input.right = False
        d.input.up = False
        d.input.down = False
        d.input.jump = False
        d.input.dodge = False
        d.input.attack = False
        d.input.ultimate = False

        if d.hitstun_timer > 0.0:
            pass
        elif d.is_dodging:
            update_dodge(d, dt)
        elif d.is_dashing:
            update_dash(d, dt)
        else:
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
        self.update_trail_effects(d, dt)

    def update(self, dt: float) -> None:
        self.update_fighter(self.player, [self.dummy], dt)
        self.update_dummy(dt)
        self.respawn_dummy_if_needed()
        self.camera.update(self.player.pos.x, self.player.pos.y)

    def draw(self, surface: pygame.Surface, dt: float, font: pygame.font.Font, draw_debug_hud_fn) -> None:
        self.renderer.draw(surface, self, dt, font, draw_debug_hud_fn)
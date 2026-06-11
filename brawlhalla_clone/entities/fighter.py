# entities/fighter.py

from __future__ import annotations

from entities.entity import Entity
from core.input_state import InputState
from core.air_resources import AirResources
from config.player_config import (
    PlayerConfig, MovementConfig, JumpConfig,
    GravityConfig, DashConfig, DodgeConfig,
)



class Fighter(Entity):
    def __init__(self, x: float, y: float, character) -> None:
        cfg = PlayerConfig()
        super().__init__(x, y, cfg.WIDTH, cfg.HEIGHT)

        self.facing = 1
        self.input = InputState()
        self.air = AirResources()

        self.is_grounded = False
        self.was_grounded = False
        self.touching_wall = False
        self.touching_ceiling = False
        self.near_ground = False

        self.is_dodging = False
        self.dodge_timer = 0.0
        self.dodge_dir_x = 0.0
        self.dodge_dir_y = 0.0
        self.dodge_kind: str | None = None

        self.air_dodge_available = True

        self.wall_dir = 0
        self.is_wall_clinging = False
        self.was_wall_clinging = False
        self.wall_detach_grace_timer = 0.0

        self.fast_falling = False
        self.move_state = "idle"

        self.pending_jump_kind: str | None = None
        self.jump_startup_timer = 0.0
        self.landing_recovery_timer = 0.0
        self.fast_fall_lock_timer = 0.0

        self.is_dashing = False
        self.dash_timer = 0.0
        self.dash_dir = 0
        self.dash_reuse_timer = 0.0
        self.left_ground_since_dash = True

        self.air = AirResources()

        self.character = character

        self.is_attacking = False
        self.current_attack = None
        self.attack_name: str | None = None
        self.attack_timer = 0.0
        self.attack_total_time = 0.0
        self.attack_has_hit = False
        self.attack_extra_fired = False
        self.attack_tick_timer = 0.0

        self.stun_timer = 0.0
        self.ultimate_timer = 0.0
        self.ultimate_ready = True

        self.move_cfg = MovementConfig()
        self.jump_cfg = JumpConfig()
        self.gravity_cfg = GravityConfig()
        self.dash_cfg = DashConfig()

        self.dodge_cooldown_timer = 0.0
        self.invuln_timer = 0.0
        self.can_attack = True

        # soft platform drop-through
        self.drop_through_timer = 0.0

    def start_attack(self, attack_data) -> None:
        self.is_attacking = True
        self.current_attack = attack_data
        self.attack_name = attack_data.name
        self.attack_timer = attack_data.total_time
        self.attack_total_time = attack_data.total_time
        self.attack_has_hit = False
        self.attack_extra_fired = False
        self.attack_tick_timer = 0.0

    def end_attack(self) -> None:
        self.is_attacking = False
        self.current_attack = None
        self.attack_name = None
        self.attack_total_time = 0.0
        self.attack_has_hit = False
        self.attack_extra_fired = False
        self.attack_tick_timer = 0.0
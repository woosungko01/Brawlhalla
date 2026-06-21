from __future__ import annotations

from entities.entity import Entity
from core.input_state import InputState
from core.air_resources import AirResources
from combat.damage_model import DamageState
from combat.pending_effects import PendingLaunch
from combat.followup_buffer import FollowupAction
from config.player_config import (
    PlayerConfig, MovementConfig, JumpConfig,
    GravityConfig, DashConfig, DodgeConfig,
)
from effects.trail_effect import TrailEffect


class Fighter(Entity):
    #캐릭터의 상태, 움직임 및 공격 제어
    def __init__(self, x: float, y: float, character) -> None:
        cfg = PlayerConfig()
        super().__init__(x, y, cfg.WIDTH, cfg.HEIGHT)

        self.attack_hit_windows: set[int] = set()

        self.facing = 1
        self.input = InputState()
        self.air = AirResources()
        self.damage = DamageState()

        self.is_grounded = False
        self.was_grounded = False
        self.touching_wall = False
        self.touching_ceiling = False
        self.near_ground = False

        self.wall_dir = 0
        self.is_wall_clinging = False
        self.was_wall_clinging = False
        self.wall_detach_grace_timer = 0.0

        self.fast_falling = False
        self.move_state = "idle"

        self.pending_jump_kind: str | None = None
        self.jump_startup_timer = 0.0
        self.fast_fall_lock_timer = 0.0

        self.is_dashing = False
        self.dash_timer = 0.0
        self.dash_dir = 0
        self.dash_reuse_timer = 0.0
        self.left_ground_since_dash = True

        self.is_dodging = False
        self.dodge_timer = 0.0
        self.dodge_dir_x = 0.0
        self.dodge_dir_y = 0.0
        self.dodge_kind: str | None = None
        self.air_dodge_available = True

        self.character = character

        self.is_attacking = False
        self.current_attack = None
        self.attack_name: str | None = None
        self.attack_timer = 0.0
        self.attack_total_time = 0.0
        self.attack_has_hit = False
        self.attack_extra_fired = False
        self.attack_tick_timer = 0.0

        self.can_attack_prestore = False
        self.stored_followup_action: FollowupAction | None = None

        self.stun_timer = 0.0
        self.hitstun_timer = 0.0
        self.pending_launch: PendingLaunch | None = None

        self.ultimate_timer = 0.0
        self.ultimate_ready = True

        self.move_cfg = MovementConfig()
        self.jump_cfg = JumpConfig()
        self.gravity_cfg = GravityConfig()
        self.dash_cfg = DashConfig()
        self.dodge_cfg = DodgeConfig()

        self.dodge_cooldown_timer = 0.0
        self.invuln_timer = 0.0
        self.can_attack = True

        self.drop_through_timer = 0.0

        self.stocks = 3
        self.is_ko = False
        self.is_dead = False

        self.spawn_x = x
        self.spawn_y = y

        self.player_index = 0
        self.is_controllable = True

        self.hit_freeze_timer = 0.0

        # knockback trail
        self.trail_effects: list[TrailEffect] = []
        self.trail_spawn_timer = 0.0

    def start_attack(self, attack_data) -> None:
        self.is_attacking = True
        self.current_attack = attack_data
        self.attack_name = attack_data.name
        self.attack_timer = attack_data.total_time
        self.attack_total_time = attack_data.total_time
        self.attack_has_hit = False
        self.attack_extra_fired = False
        self.attack_tick_timer = 0.0
        self.attack_hit_windows = set()

        self.can_attack_prestore = False
        self.stored_followup_action = None

    def end_attack(self) -> None:
        self.is_attacking = False
        self.current_attack = None
        self.attack_name = None
        self.attack_total_time = 0.0
        self.attack_has_hit = False
        self.attack_extra_fired = False
        self.attack_tick_timer = 0.0
        self.attack_hit_windows = set()

    def reset_combat_state(self) -> None:
        self.end_attack()

        self.can_attack_prestore = False
        self.stored_followup_action = None

        self.stun_timer = 0.0
        self.hitstun_timer = 0.0
        self.pending_launch = None
        self.hit_freeze_timer = 0.0

        self.is_dashing = False
        self.dash_timer = 0.0
        self.dash_dir = 0

        self.is_dodging = False
        self.dodge_timer = 0.0
        self.dodge_dir_x = 0.0
        self.dodge_dir_y = 0.0
        self.dodge_kind = None

        self.is_wall_clinging = False
        self.was_wall_clinging = False
        self.wall_dir = 0
        self.wall_detach_grace_timer = 0.0

        self.pending_jump_kind = None
        self.jump_startup_timer = 0.0

        self.fast_falling = False
        self.fast_fall_lock_timer = 0.0

        self.trail_effects.clear()
        self.trail_spawn_timer = 0.0

    def respawn_at(self, x: float, y: float, invuln_time: float = 3.0) -> None:
        self.pos.x = x
        self.pos.y = y
        self.vel.x = 0.0
        self.vel.y = 0.0

        self.damage.percent = 0.0
        self.invuln_timer = invuln_time

        self.is_ko = False
        self.is_dead = False

        self.is_grounded = False
        self.was_grounded = False
        self.near_ground = False
        self.touching_wall = False
        self.touching_ceiling = False

        self.air.reset()
        self.air_dodge_available = True
        self.left_ground_since_dash = True

        self.hit_freeze_timer = 0.0
        self.trail_effects.clear()
        self.trail_spawn_timer = 0.0
        self.reset_combat_state()
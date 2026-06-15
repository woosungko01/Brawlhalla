# entities/fighter.py
# 전투 가능한 엔티티(Fighter) 정의 파일
# - 이동/점프/대시/회피/공격 상태
# - 데미지/피격 상태
# - 2인 대전용 stocks / KO / respawn 상태 포함

from __future__ import annotations

from entities.entity import Entity
from core.input_state import InputState
from core.air_resources import AirResources
from combat.damage_model import DamageState
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

        self.stun_timer = 0.0
        self.hitstun_timer = 0.0
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

        # ── 로컬 2인 대전용 상태 ─────────────────────────────
        self.stocks = 3
        self.is_ko = False
        self.is_dead = False

        # 리스폰 위치 기준용
        self.spawn_x = x
        self.spawn_y = y

        # 1P / 2P 표시용
        self.player_index = 0

        # 조작 가능 여부
        self.is_controllable = True

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

    def reset_combat_state(self) -> None:
        """리스폰 등에서 호출: 공격/피격/이동 특수상태 초기화"""
        self.end_attack()

        self.stun_timer = 0.0
        self.hitstun_timer = 0.0

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

    def respawn_at(self, x: float, y: float, invuln_time: float = 3.0) -> None:
        """지정 위치에 리스폰하고 데미지/공중 자원 등을 초기화"""
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

        self.reset_combat_state()
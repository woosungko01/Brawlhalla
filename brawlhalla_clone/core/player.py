# core/player.py

from core.vec2 import Vec2
from core.input_state import InputState
from core.air_resources import AirResources
from config.player_config import (
    PlayerConfig, MovementConfig, JumpConfig,
    GravityConfig, DashConfig,
)


class Player:
    def __init__(self) -> None:
        cfg = PlayerConfig()

        self.pos = Vec2(cfg.SPAWN_X, cfg.SPAWN_Y)
        self.vel = Vec2(0.0, 0.0)

        self.width = cfg.WIDTH
        self.height = cfg.HEIGHT

        self.facing = 1

        self.is_grounded = False
        self.was_grounded = False
        self.touching_wall = False
        self.touching_ceiling = False
        self.near_ground = False

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

        # 캐릭터 종류: "brawler" | "swordsman"
        self.character_id = "brawler"

        # 전투
        self.is_attacking = False
        self.attack_name: str | None = None
        self.attack_timer = 0.0
        self.attack_total_time = 0.0
        self.attack_has_hit = False
        self.attack_extra_fired = False

        # 카운터 성공 효과용
        self.stun_timer = 0.0

        # 궁극기
        self.ultimate_timer = 0.0
        self.ultimate_ready = True   # 실험용

        self.move_cfg = MovementConfig()
        self.jump_cfg = JumpConfig()
        self.gravity_cfg = GravityConfig()
        self.dash_cfg = DashConfig()

        self.dodge_cooldown_timer = 0.0
        self.invuln_timer = 0.0
        self.can_attack = True

        self.input = InputState()

    @property
    def rect_x(self) -> float:
        return self.pos.x - self.width / 2

    @property
    def rect_y(self) -> float:
        return self.pos.y - self.height / 2

    @property
    def bottom(self) -> float:
        return self.pos.y + self.height / 2

    @property
    def right(self) -> float:
        return self.pos.x + self.width / 2

    @property
    def left(self) -> float:
        return self.pos.x - self.width / 2

    @property
    def top(self) -> float:
        return self.pos.y - self.height / 2
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

        # 위치 / 속도
        self.pos = Vec2(cfg.SPAWN_X, cfg.SPAWN_Y)
        self.vel = Vec2(0.0, 0.0)

        # 크기
        self.width: int = cfg.WIDTH
        self.height: int = cfg.HEIGHT

        # 방향
        self.facing: int = 1

        # 접지 / 벽 / 천장
        self.is_grounded: bool = False
        self.was_grounded: bool = False
        self.touching_wall: bool = False
        self.touching_ceiling: bool = False
        self.near_ground: bool = False

        # 이동 플래그
        self.fast_falling: bool = False

        # 이동 상태
        self.move_state: str = "idle"

        # 점프
        self.pending_jump_kind: str | None = None

        # 타이머
        self.jump_startup_timer: float = 0.0
        self.landing_recovery_timer: float = 0.0
        self.fast_fall_lock_timer: float = 0.0

        # 대시
        self.is_dashing: bool = False
        self.dash_timer: float = 0.0
        self.dash_dir: int = 0
        self.dash_reuse_timer: float = 0.0
        self.left_ground_since_dash: bool = True

        # 공중 자원
        self.air = AirResources()

        # 전투 상태
        self.is_attacking: bool = False
        self.attack_name: str | None = None
        self.attack_timer: float = 0.0
        self.attack_total_time: float = 0.0
        self.attack_has_hit: bool = False

        # 궁극기
        self.ultimate_timer: float = 0.0
        self.ultimate_ready: bool = True   # 실험용으로 항상 가능하게 시작

        # 설정
        self.move_cfg = MovementConfig()
        self.jump_cfg = JumpConfig()
        self.gravity_cfg = GravityConfig()
        self.dash_cfg = DashConfig()

        # 확장 슬롯
        self.dodge_cooldown_timer: float = 0.0
        self.invuln_timer: float = 0.0
        self.can_attack: bool = True

        # 입력
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
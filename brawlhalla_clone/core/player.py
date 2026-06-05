# core/player.py

from core.vec2          import Vec2
from core.input_state   import InputState
from core.air_resources import AirResources
from config.player_config import (
    PlayerConfig, MovementConfig, JumpConfig,
    GravityConfig, DashConfig,
)


class Player:
    """
    플레이어 엔티티.

    데이터만 보관하고, 실제 로직은 systems/ 아래 각 시스템이 담당한다.
    새 기능을 추가할 때는 여기에 상태 변수를 추가하고,
    시스템 파일에 처리 함수를 만들면 된다.
    """

    def __init__(self) -> None:
        cfg = PlayerConfig()

        # ── 위치 / 속도 ────────────────────────────────
        self.pos = Vec2(cfg.SPAWN_X, cfg.SPAWN_Y)
        self.vel = Vec2(0.0, 0.0)

        # ── 크기 ───────────────────────────────────────
        self.width:  int = cfg.WIDTH
        self.height: int = cfg.HEIGHT

        # ── 방향 (1=오른쪽, -1=왼쪽) ───────────────────
        self.facing: int = 1

        # ── 지면 / 벽 접촉 상태 ────────────────────────
        self.is_grounded:    bool = False
        self.was_grounded:   bool = False   # 이전 프레임 grounded
        self.touching_wall:  bool = False
        self.touching_ceiling: bool = False

        # ── 특수 이동 플래그 ────────────────────────────
        self.fast_falling: bool = False

        # ── 이동 상태 (state machine) ───────────────────
        # 가능 값:
        # "idle" | "run" | "jump_startup" | "dash_startup" |
        # "airborne" | "landing" | "dashing"
        self.move_state: str = "idle"

        # ── 점프 예약 ───────────────────────────────────
        # "ground" | "air" | None
        self.pending_jump_kind: str | None = None

        # ── 타이머 ─────────────────────────────────────
        self.jump_startup_timer: float = 0.0
        self.landing_recovery_timer: float = 0.0
        self.fast_fall_lock_timer: float = 0.0

        # ── 대시 상태 ───────────────────────────────────
        self.is_dashing: bool = False
        self.dash_timer: float = 0.0
        self.dash_dir: int = 0

        # dash 재사용 제한
        self.dash_reuse_timer: float = 0.0

        # 직전 dash 이후 공중에 떴는가
        self.left_ground_since_dash: bool = True

        # 지면 근처 공중 판정
        self.near_ground: bool = False

        # ── 공중 자원 ───────────────────────────────────
        self.air = AirResources()

        # ── 설정값 (시스템에서 참조) ────────────────────
        self.move_cfg    = MovementConfig()
        self.jump_cfg    = JumpConfig()
        self.gravity_cfg = GravityConfig()
        self.dash_cfg    = DashConfig()

        # ── 확장 예약 슬롯 ──────────────────────────────
        # 나중에 공격 / 회피 / 무적 등을 붙일 자리
        self.dodge_cooldown_timer: float = 0.0
        self.invuln_timer:         float = 0.0
        self.can_attack:           bool  = True

    # ── 편의 프로퍼티 ──────────────────────────────────────

    @property
    def rect_x(self) -> float:
        """히트박스 좌측 x (중심 기준)"""
        return self.pos.x - self.width / 2

    @property
    def rect_y(self) -> float:
        """히트박스 상단 y (중심 기준)"""
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

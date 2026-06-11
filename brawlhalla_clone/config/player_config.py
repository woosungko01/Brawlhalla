# config/player_config.py
#
# ╔══════════════════════════════════════════════════════╗
# ║  수치 튜닝은 이 파일에서만 하면 됩니다.               ║
# ╚══════════════════════════════════════════════════════╝


class MovementConfig:
    """수평 이동 관련 수치"""

    # 가속도 (pixels/sec²)
    GROUND_ACCEL: float = 5000.0
    AIR_ACCEL: float = 2800.0

    # 감속 (pixels/sec²)
    GROUND_FRICTION: float = 4500.0
    AIR_DRAG: float = 150.0

    # 최대 속도 (pixels/sec)
    MAX_RUN_SPEED: float = 600.0
    MAX_AIR_SPEED: float = 600.0


class JumpConfig:
    """점프 관련 수치"""

    # 점프력 (pixels/sec, 위 방향이 음수)
    JUMP_SPEED: float = 1100.0

    # 다중 점프 횟수 (지상 점프 제외, 순수 공중 추가 점프 수)
    MAX_AIR_JUMPS: int = 2

    # 스타트업 딜레이 (sec)
    JUMP_STARTUP_TIME: float = 0.04

    # 점프 직후 fast fall을 아주 잠깐 막는 시간
    FAST_FALL_LOCK_TIME: float = 0.045


class GravityConfig:
    """중력 / 낙하 관련 수치"""

    GRAVITY: float = 3000.0
    MAX_FALL_SPEED: float = 700.0

    FAST_FALL_ACCEL_BONUS: float = 5000.0
    FAST_FALL_TERMINAL_SPEED: float = 1100.0

    # 벽에 붙어 있을 때 최대 미끄러짐 속도
    WALL_SLIDE_SPEED: float = 180.0
    WALL_DETACH_GRACE_TIME: float = 0.06


class DashConfig:
    """대시 관련 수치"""

    # 대시 지속 시간
    DASH_TIME: float = 0.12

    # 대시 속도
    DASH_SPEED: float = 1000.0
    SPRINT_SPEED: float = 800.0

    # 연속 지상 dash 재사용 제한
    GROUND_CHAIN_REUSE: float = 25 / 60

    # 공중을 거친 후 다시 dash할 때 재사용 제한
    AIR_RESET_REUSE: float = 0.0

    # 땅 근처 snap dash 허용 거리
    GROUND_SNAP_DIST: float = 50.0

class PlayerConfig:
    """플레이어 물리 크기 등 기본 설정"""

    WIDTH: int = 48
    HEIGHT: int = 64

    SPAWN_X: float = 400.0
    SPAWN_Y: float = 200.0


class DodgeConfig:
    """회피(dodge) 관련 수치"""

    # 지상/공중 spot dodge 지속
    SPOT_DODGE_TIME: float = 0.22
    SPOT_DODGE_INVULN_TIME: float = 0.22

    # 공중 방향 dodge 지속
    AIR_DODGE_TIME: float = 0.20
    AIR_DODGE_INVULN_TIME: float = 0.20

    # 공중 방향 dodge 고정 이동 속도
    AIR_DODGE_SPEED: float = 780.0
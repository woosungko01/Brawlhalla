# Brawlhalla Clone - 이동 시스템 프로토타입

## 프로젝트 구조

```
brawlhalla_clone/
├── main.py               # 게임 진입점
├── config/
│   └── player_config.py  # ← 수치 튜닝은 여기서만!
├── core/
│   ├── vec2.py           # 2D 벡터
│   ├── input_state.py    # 입력 상태
│   ├── air_resources.py  # 공중 자원 (점프 횟수 등)
│   └── player.py         # 플레이어 엔티티
├── systems/
│   ├── movement.py       # 수평 이동 처리
│   ├── jump.py           # 점프 / 다중점프 처리
│   ├── gravity.py        # 중력 / 패스트폴 처리
│   ├── dash.py           # 대시 처리
│   ├── collision.py      # 충돌 감지 및 grounded 판정
│   └── state_machine.py  # 이동 상태 갱신
└── utils/
    └── debug_hud.py      # 디버그 정보 출력
```

## 실행 방법

```bash
pip install pygame
python main.py
```

## 조작 키

| 키 | 동작 |
|---|---|
| A / D 또는 ← / → | 좌우 이동 |
| Space 또는 W / ↑ | 점프 (최대 3회) |
| S / ↓ | 패스트폴 (공중에서) |
| Shift + 방향키 | 대시 |
| F1 | 디버그 HUD 토글 |

## 튜닝 가이드

`config/player_config.py`만 수정하면 됩니다.
- `MovementConfig` : 이동속도, 가속도, 마찰
- `JumpConfig`     : 점프력, 횟수, 스타트업 딜레이
- `GravityConfig`  : 중력, 낙하속도, 패스트폴
- `DashConfig`     : 대시 속도, 시간, 스프린트 속도

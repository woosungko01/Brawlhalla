# core/input_state.py


class InputState:
    """
    한 프레임의 입력 상태.

    *_pressed  : 이번 프레임에 처음 눌린 경우만 True
    *_released : 이번 프레임에 떼어진 경우만 True
    held       : 현재 누르고 있는 상태
    """

    __slots__ = (
        "left", "right", "up", "down",
        "jump", "jump_pressed", "jump_released",
        "dodge", "dodge_pressed",
    )

    def __init__(self) -> None:
        # 현재 누르고 있는지
        self.left:  bool = False
        self.right: bool = False
        self.up:    bool = False
        self.down:  bool = False
        self.jump:  bool = False
        self.dodge: bool = False

        # 이번 프레임 이벤트
        self.jump_pressed:   bool = False
        self.jump_released:  bool = False
        self.dodge_pressed:  bool = False

    def reset_frame_events(self) -> None:
        """매 프레임 시작 시 1프레임 이벤트 초기화"""
        self.jump_pressed  = False
        self.jump_released = False
        self.dodge_pressed = False

    @property
    def move_x(self) -> int:
        """수평 입력 방향. -1 / 0 / 1"""
        return int(self.right) - int(self.left)

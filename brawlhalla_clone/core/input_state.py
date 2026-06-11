# core/input_state.py

class InputState:
    """
    한 프레임의 입력 상태.

    *_pressed  : 이번 프레임에 처음 눌린 경우만 True
    *_released : 이번 프레임에 떼어진 경우만 True
    """

    __slots__ = (
        "left", "right", "up", "down",
        "jump", "jump_pressed", "jump_released",
        "dodge", "dodge_pressed",
        "attack", "attack_pressed",
        "ultimate", "ultimate_pressed",
    )

    def __init__(self) -> None:
        self.left: bool = False
        self.right: bool = False
        self.up: bool = False
        self.down: bool = False

        self.jump: bool = False
        self.jump_pressed: bool = False
        self.jump_released: bool = False

        self.dodge: bool = False
        self.dodge_pressed: bool = False

        self.attack: bool = False
        self.attack_pressed: bool = False

        self.ultimate: bool = False
        self.ultimate_pressed: bool = False

    def reset_frame_events(self) -> None:
        self.jump_pressed = False
        self.jump_released = False
        self.dodge_pressed = False
        self.attack_pressed = False
        self.ultimate_pressed = False

    @property
    def move_x(self) -> int:
        return int(self.right) - int(self.left)
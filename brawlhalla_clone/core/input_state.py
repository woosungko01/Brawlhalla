# core/input_state.py

class InputState:
    #입력된 정보 인식
    __slots__ = (
        "left", "right", "up", "down",
        "jump", "jump_pressed", "jump_released",
        "dodge", "dodge_pressed",
        "attack", "attack_pressed",
        "ultimate", "ultimate_pressed",
    )

    def __init__(self) -> None:
        self.left = False
        self.right = False
        self.up = False
        self.down = False

        self.jump = False
        self.jump_pressed = False
        self.jump_released = False

        self.dodge = False
        self.dodge_pressed = False

        self.attack = False
        self.attack_pressed = False

        self.ultimate = False
        self.ultimate_pressed = False

    def reset_frame_events(self) -> None:
        self.jump_pressed = False
        self.jump_released = False
        self.dodge_pressed = False
        self.attack_pressed = False
        self.ultimate_pressed = False

    @property
    def move_x(self) -> int:
        return int(self.right) - int(self.left)
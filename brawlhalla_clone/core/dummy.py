# core/dummy.py

from core.vec2 import Vec2


class Dummy:
    def __init__(self, x: float, y: float) -> None:
        self.pos = Vec2(x, y)
        self.vel = Vec2(0.0, 0.0)

        self.width = 52
        self.height = 72

        self.hitstun_timer = 0.0

    @property
    def rect_x(self) -> float:
        return self.pos.x - self.width / 2

    @property
    def rect_y(self) -> float:
        return self.pos.y - self.height / 2

    @property
    def bottom(self) -> float:
        return self.pos.y + self.height / 2
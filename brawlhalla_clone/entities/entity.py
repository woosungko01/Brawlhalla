#entities/entity.py

from core.vec2 import Vec2


class Entity:
    def __init__(self, x: float, y: float, width: int, height: int) -> None:
        self.pos = Vec2(x, y)
        self.vel = Vec2(0.0, 0.0)
        self.width = width
        self.height = height

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
    def top(self) -> float:
        return self.pos.y - self.height / 2

    @property
    def left(self) -> float:
        return self.pos.x - self.width / 2

    @property
    def right(self) -> float:
        return self.pos.x + self.width / 2
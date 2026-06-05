# core/vec2.py


class Vec2:
    """2D 벡터. x, y 좌표 또는 속도를 나타냄."""

    __slots__ = ("x", "y")

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Vec2({self.x:.1f}, {self.y:.1f})"

    def copy(self) -> "Vec2":
        return Vec2(self.x, self.y)

    def reset(self) -> None:
        self.x = 0.0
        self.y = 0.0

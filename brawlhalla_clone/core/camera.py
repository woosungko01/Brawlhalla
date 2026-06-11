# core/camera.py
#
# 월드 좌표를 화면 좌표로 변환하기 위한 카메라.
# 플레이어 중심을 부드럽게 따라가며, 월드 경계를 벗어나지 않도록 clamp 한다.

class Camera:
    def __init__(self, screen_w: int, screen_h: int,
                 world_w: int, world_h: int) -> None:
        self.x: float = 0.0
        self.y: float = 0.0

        self.screen_w = screen_w
        self.screen_h = screen_h
        self.world_w = world_w
        self.world_h = world_h

        # 따라가는 강도 (0~1 사이, 높을수록 더 빨리 따라감)
        self.follow_x: float = 0.12
        self.follow_y: float = 0.10

    def update(self, target_x: float, target_y: float) -> None:
        """
        target(보통 플레이어 중심)를 향해 부드럽게 이동.
        """
        desired_x = target_x - self.screen_w / 2
        desired_y = (target_y - 40) - self.screen_h / 2

        self.x += (desired_x - self.x) * self.follow_x
        self.y += (desired_y - self.y) * self.follow_y

        self.clamp_to_world()

    def clamp_to_world(self) -> None:
        max_x = max(0.0, self.world_w - self.screen_w)
        max_y = max(0.0, self.world_h - self.screen_h)

        if self.x < 0.0:
            self.x = 0.0
        elif self.x > max_x:
            self.x = max_x

        if self.y < 0.0:
            self.y = 0.0
        elif self.y > max_y:
            self.y = max_y

    def world_to_screen(self, x: float, y: float) -> tuple[int, int]:
        return int(x - self.x), int(y - self.y)
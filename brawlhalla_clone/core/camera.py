# core/camera.py
# 1인 추적 + 2인 추적 + 데미지 기반 zoom out 지원 카메라 파일

class Camera:
    def __init__(self, screen_w: int, screen_h: int,
                 world_w: int, world_h: int) -> None:
        self.x: float = 0.0
        self.y: float = 0.0

        self.screen_w = screen_w
        self.screen_h = screen_h
        self.world_w = world_w
        self.world_h = world_h

        # 따라가는 강도
        self.follow_x: float = 0.12
        self.follow_y: float = 0.10

        # zoom
        # 1.0 = 기본, 낮을수록 더 넓게 보임(zoom out)
        self.zoom: float = 1.0
        self.target_zoom: float = 1.0
        self.zoom_lerp: float = 0.10

        self.min_zoom: float = 0.60
        self.max_zoom: float = 1.15

    def update(self, target_x: float, target_y: float) -> None:
        """기본 1인 추적"""
        desired_x = target_x - (self.screen_w / self.zoom) / 2
        desired_y = (target_y - 40) - (self.screen_h / self.zoom) / 2

        self.x += (desired_x - self.x) * self.follow_x
        self.y += (desired_y - self.y) * self.follow_y

        self._update_zoom()
        self.clamp_to_world()

    def set_dual_target(self, x1: float, y1: float, x2: float, y2: float) -> None:
        """두 플레이어의 중간 지점을 기준으로 카메라 이동"""
        mid_x = (x1 + x2) * 0.5
        mid_y = (y1 + y2) * 0.5

        desired_x = mid_x - (self.screen_w / self.zoom) / 2
        desired_y = (mid_y - 40) - (self.screen_h / self.zoom) / 2

        self.x += (desired_x - self.x) * self.follow_x
        self.y += (desired_y - self.y) * self.follow_y

        self._update_zoom()
        self.clamp_to_world()

    def set_target_zoom_from_damage(self, max_percent: float) -> None:
        self.target_zoom = 1.0

    def _update_zoom(self) -> None:
        self.zoom += (self.target_zoom - self.zoom) * self.zoom_lerp

        if self.zoom < self.min_zoom:
            self.zoom = self.min_zoom
        elif self.zoom > self.max_zoom:
            self.zoom = self.max_zoom

    def clamp_to_world(self) -> None:
        visible_w = self.screen_w / self.zoom
        visible_h = self.screen_h / self.zoom

        max_x = max(0.0, self.world_w - visible_w)
        max_y = max(0.0, self.world_h - visible_h)

        if self.x < 0.0:
            self.x = 0.0
        elif self.x > max_x:
            self.x = max_x

        if self.y < 0.0:
            self.y = 0.0
        elif self.y > max_y:
            self.y = max_y

    def world_to_screen(self, x: float, y: float) -> tuple[int, int]:
        sx = (x - self.x) * self.zoom
        sy = (y - self.y) * self.zoom
        return int(sx), int(sy)
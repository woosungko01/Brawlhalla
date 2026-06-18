class Camera:
    def __init__(self, screen_w: int, screen_h: int,
                 world_w: int, world_h: int) -> None:
        self.x: float = 0.0
        self.y: float = 0.0

        self.screen_w = screen_w
        self.screen_h = screen_h
        self.world_w = world_w
        self.world_h = world_h

        # 카메라 이동 추적 속도
        self.follow_x: float = 0.18
        self.follow_y: float = 0.16

        # 기본 줌
        self.zoom: float = 1.55
        self.target_zoom: float = 1.55
        self.zoom_lerp: float = 0.18

        # 시스템상 허용 최소/최대 줌
        self.min_zoom: float = 0.45
        self.max_zoom: float = 1.75

        # 기본 듀얼 프레이밍 여유값
        self.dual_margin_x: float = 220.0
        self.dual_margin_y: float = 180.0

    def update(self, target_x: float, target_y: float) -> None:
        self.target_zoom = self.max_zoom
        self._update_zoom()

        desired_x = target_x - (self.screen_w / self.zoom) / 2
        desired_y = (target_y - 40) - (self.screen_h / self.zoom) / 2

        self.x += (desired_x - self.x) * self.follow_x
        self.y += (desired_y - self.y) * self.follow_y

        self.clamp_to_world()

    def set_dual_target(self, x1: float, y1: float, x2: float, y2: float) -> None:
        mid_x = (x1 + x2) * 0.5
        mid_y = (y1 + y2) * 0.5

        self._set_target_zoom_to_fit_points(x1, y1, x2, y2)
        self._update_zoom()

        visible_w = self.screen_w / self.zoom
        visible_h = self.screen_h / self.zoom

        desired_x = mid_x - visible_w / 2
        desired_y = (mid_y - 40) - visible_h / 2

        self.x += (desired_x - self.x) * self.follow_x
        self.y += (desired_y - self.y) * self.follow_y

        self.clamp_to_world()

    def _get_world_safe_min_zoom(self) -> float:
        # 화면 전체가 월드 안에 들어오려면
        # visible_w = screen_w / zoom <= world_w
        # visible_h = screen_h / zoom <= world_h
        # => zoom >= screen_w / world_w
        # => zoom >= screen_h / world_h
        safe_zoom_x = self.screen_w / self.world_w
        safe_zoom_y = self.screen_h / self.world_h
        return max(safe_zoom_x, safe_zoom_y)

    def _get_effective_min_zoom(self) -> float:
        return max(self.min_zoom, self._get_world_safe_min_zoom())

    def _set_target_zoom_to_fit_points(self, x1: float, y1: float, x2: float, y2: float) -> None:
        dist_x = abs(x2 - x1)
        dist_y = abs(y2 - y1)
        distance = (dist_x * dist_x + dist_y * dist_y) ** 0.5

        # 멀어질수록 프레이밍 여유를 조금 더 둠
        dynamic_margin_x = self.dual_margin_x + distance * 0.18
        dynamic_margin_y = self.dual_margin_y + distance * 0.10

        span_x = max(1.0, dist_x + dynamic_margin_x)
        span_y = max(1.0, dist_y + dynamic_margin_y)

        zoom_x = self.screen_w / span_x
        zoom_y = self.screen_h / span_y

        fit_zoom = min(zoom_x, zoom_y)

        # 거리 커질수록 체감상 더 빨리 줌아웃
        extra_zoom_out = 1.0

        if distance > 250.0:
            extra_zoom_out *= 0.94
        if distance > 450.0:
            extra_zoom_out *= 0.90
        if distance > 700.0:
            extra_zoom_out *= 0.86
        if distance > 950.0:
            extra_zoom_out *= 0.82

        desired_zoom = fit_zoom * extra_zoom_out

        effective_min_zoom = self._get_effective_min_zoom()

        if desired_zoom < effective_min_zoom:
            desired_zoom = effective_min_zoom
        elif desired_zoom > self.max_zoom:
            desired_zoom = self.max_zoom

        self.target_zoom = desired_zoom

    def _update_zoom(self) -> None:
        self.zoom += (self.target_zoom - self.zoom) * self.zoom_lerp

        effective_min_zoom = self._get_effective_min_zoom()

        if self.zoom < effective_min_zoom:
            self.zoom = effective_min_zoom
        elif self.zoom > self.max_zoom:
            self.zoom = self.max_zoom

    def clamp_to_world(self) -> None:
        effective_min_zoom = self._get_effective_min_zoom()

        if self.zoom < effective_min_zoom:
            self.zoom = effective_min_zoom
        elif self.zoom > self.max_zoom:
            self.zoom = self.max_zoom

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
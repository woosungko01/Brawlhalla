import os
import random
import pygame

from rendering.fighter_renderer import FighterRenderer


class CleanMatchRenderer:
    BG_COLOR = (30, 30, 45)

    PLAYER1_COLOR = (100, 180, 255)
    PLAYER1_BORDER = (60, 140, 220)

    PLAYER2_COLOR = (255, 170, 110)
    PLAYER2_BORDER = (220, 120, 70)

    def __init__(self) -> None:
        self.fighter_renderer = FighterRenderer()
        self._background_cache: dict[str, pygame.Surface] = {}
        self.trail_image = self._load_trail_image()

    def _load_trail_image(self) -> pygame.Surface | None:
        path = os.path.join("assets", "effects", "knockback_trail.png")
        if not os.path.exists(path):
            return None

        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error:
            return None

    def draw(self, surface: pygame.Surface, match, dt: float, font: pygame.font.Font, draw_debug_hud_fn) -> None:
        surface.fill(self.BG_COLOR)

        original_cam_x = match.camera.x
        original_cam_y = match.camera.y

        if getattr(match, "camera_shake_timer", 0.0) > 0.0:
            strength = getattr(match, "camera_shake_strength", 0.0)
            match.camera.x += random.uniform(-strength, strength)
            match.camera.y += random.uniform(-strength, strength)

        self._draw_background(surface, match)

        self._draw_trail_effects(surface, match.player1, match.camera)
        self._draw_trail_effects(surface, match.player2, match.camera)

        self.fighter_renderer.update(match.player1, dt)
        self.fighter_renderer.update(match.player2, dt)

        self.fighter_renderer.draw(
            surface, match.player1, match.camera,
            self.PLAYER1_COLOR, self.PLAYER1_BORDER
        )
        self.fighter_renderer.draw(
            surface, match.player2, match.camera,
            self.PLAYER2_COLOR, self.PLAYER2_BORDER
        )

        self._draw_vs_ui(surface, match, font)
        self._draw_ko_banner(surface, match)

        match.camera.x = original_cam_x
        match.camera.y = original_cam_y

    def _draw_background(self, surface: pygame.Surface, match) -> None:
        bg_path = getattr(match.stage, "background_path", None)
        if not bg_path:
            return

        bg = self._load_background(bg_path)
        if bg is None:
            return

        sx, sy = match.camera.world_to_screen(0, 0)
        scaled = pygame.transform.scale(
            bg,
            (
                int(match.stage.world_w * match.camera.zoom),
                int(match.stage.world_h * match.camera.zoom),
            ),
        )
        surface.blit(scaled, (sx, sy))

    def _load_background(self, path: str) -> pygame.Surface | None:
        if path in self._background_cache:
            return self._background_cache[path]

        if not os.path.exists(path):
            return None

        try:
            img = pygame.image.load(path).convert()
        except pygame.error:
            return None

        self._background_cache[path] = img
        return img

    def _draw_trail_effects(self, surface: pygame.Surface, fighter, camera) -> None:
        if self.trail_image is None:
            return

        for fx in fighter.trail_effects:
            ratio = fx.lifetime / fx.max_lifetime if fx.max_lifetime > 0.0 else 0.0
            alpha = int(150 * ratio)
            scale = fx.scale * (0.60 + 0.05 * ratio)

            w = max(8, int(self.trail_image.get_width() * scale * camera.zoom))
            h = max(8, int(self.trail_image.get_height() * scale * camera.zoom))

            sprite = pygame.transform.smoothscale(self.trail_image, (w, h)).copy()
            sprite.set_alpha(alpha)

            sx, sy = camera.world_to_screen(fx.x, fx.y)
            draw_x = sx - w // 2
            draw_y = sy - h // 2

            surface.blit(sprite, (draw_x, draw_y))

    def _lerp_color(self, a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
        t = max(0.0, min(1.0, t))
        return (
            int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t),
        )

    def _draw_damage_meter(
        self,
        surface: pygame.Surface,
        *,
        x: int,
        y: int,
        w: int,
        h: int,
        fighter,
        label: str,
        align_right: bool = False,
    ) -> None:
        damage = max(0.0, float(fighter.damage.percent))
        fill_ratio = min(damage / 300.0, 1.0)

        bar_color = self._lerp_color((70, 150, 255), (255, 60, 60), fill_ratio)

        panel_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, (20, 24, 32), panel_rect, border_radius=10)
        pygame.draw.rect(surface, (90, 100, 120), panel_rect, 2, border_radius=10)

        inner_margin = 6
        inner_rect = panel_rect.inflate(-inner_margin * 2, -inner_margin * 2)
        pygame.draw.rect(surface, (35, 40, 52), inner_rect, border_radius=8)

        fill_w = int(inner_rect.width * fill_ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(inner_rect.x, inner_rect.y, fill_w, inner_rect.height)
            pygame.draw.rect(surface, bar_color, fill_rect, border_radius=8)

        small_font = pygame.font.SysFont("monospace", 14, bold=True)
        value_font = pygame.font.SysFont("monospace", 18, bold=True)

        label_surf = small_font.render(label, True, (235, 235, 235))
        value_color = self._lerp_color((160, 210, 255), (255, 90, 90), fill_ratio)
        value_surf = value_font.render(f"{damage:.1f}%", True, value_color)
        stock_surf = small_font.render(f"STOCKS {fighter.stocks}", True, (220, 220, 220))

        if align_right:
            surface.blit(label_surf, (panel_rect.right - label_surf.get_width(), panel_rect.y - 44))
            surface.blit(value_surf, (panel_rect.right - value_surf.get_width(), panel_rect.y - 24))
            surface.blit(stock_surf, (panel_rect.right - stock_surf.get_width(), panel_rect.bottom + 6))
        else:
            surface.blit(label_surf, (panel_rect.x, panel_rect.y - 44))
            surface.blit(value_surf, (panel_rect.x, panel_rect.y - 24))
            surface.blit(stock_surf, (panel_rect.x, panel_rect.bottom + 6))

    def _draw_vs_ui(self, surface: pygame.Surface, match, font: pygame.font.Font) -> None:
        p1 = match.player1
        p2 = match.player2

        meter_w = 260
        meter_h = 24
        right_margin = 20
        top_margin = 20
        meter_gap = 70

        meter_x = surface.get_width() - meter_w - right_margin

        self._draw_damage_meter(
            surface,
            x=meter_x,
            y=top_margin,
            w=meter_w,
            h=meter_h,
            fighter=p1,
            label=f"P1 {p1.character.character_id.upper()}",
            align_right=True,
        )

        self._draw_damage_meter(
            surface,
            x=meter_x,
            y=top_margin + meter_gap,
            w=meter_w,
            h=meter_h,
            fighter=p2,
            label=f"P2 {p2.character.character_id.upper()}",
            align_right=True,
        )

        if p1.ultimate_timer > 0.0:
            ult1 = font.render("P1 ULT ACTIVE", True, (255, 220, 120))
            surface.blit(ult1, (20, 20))

        if p2.ultimate_timer > 0.0:
            ult2 = font.render("P2 ULT ACTIVE", True, (255, 220, 120))
            surface.blit(ult2, (20, 44))

        if getattr(match, "is_match_over", False) and getattr(match, "winner", None) is not None:
            win_surf = font.render(
                f"P{match.winner.player_index} WIN!",
                True,
                (255, 240, 120),
            )
            surface.blit(
                win_surf,
                (
                    surface.get_width() // 2 - win_surf.get_width() // 2,
                    20,
                ),
            )

    def _draw_ko_banner(self, surface: pygame.Surface, match) -> None:
        text = getattr(match, "ko_banner_text", None)
        timer = getattr(match, "ko_banner_timer", 0.0)

        if not text or timer <= 0.0:
            return

        color = (255, 90, 90)
        if "P2" in text:
            color = (255, 170, 110)

        banner_font = pygame.font.SysFont("monospace", 30, bold=True)
        text_surf = banner_font.render(text, True, color)
        shadow_surf = banner_font.render(text, True, (20, 20, 20))

        x = surface.get_width() // 2 - text_surf.get_width() // 2
        y = 18

        surface.blit(shadow_surf, (x + 3, y + 3))
        surface.blit(text_surf, (x, y))
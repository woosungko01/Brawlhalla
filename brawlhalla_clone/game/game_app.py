import os
import sys
import pygame

from core.input_state import InputState
from game.training_match import TrainingMatch
from game.local_vs_match import LocalVsMatch
from game.real_vs_match import RealVsMatch
from utils.debug_hud import draw_debug_hud
from rendering.fighter_renderer import FighterRenderer


class GameApp:
    # 기본적인 게임 구조
    FPS = 60
    TITLE = "BROHALLA"

    CHAR_OPTIONS = ["brawler", "swordsman", "gunner"]

    def __init__(self) -> None:
        pygame.init()

        info = pygame.display.Info()
        self.SCREEN_W = info.current_w - 16
        self.SCREEN_H = info.current_h - 80

        self.screen = pygame.display.set_mode(
            (self.SCREEN_W, self.SCREEN_H),
            pygame.RESIZABLE
        )
        pygame.display.set_caption(self.TITLE)

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 13)
        self.mid_font = pygame.font.SysFont("monospace", 18)
        self.big_font = pygame.font.SysFont("monospace", 26, bold=True)
        self.countdown_font = pygame.font.SysFont("monospace", 54, bold=True)

        self.scene = "mode_select"
        self.match = None
        self.vs_mode_type = "local"

        self.match_countdown_active = False
        self.match_countdown_timer = 0.0
        self.match_countdown_duration = 4.0

        self.p1_choice_index = 0
        self.p2_choice_index = 1
        self.p1_locked = False
        self.p2_locked = False

        self.char_select_anim_time = 0.0
        self.menu_anim_time = 0.0

        self.char_select_frames: dict[str, list[pygame.Surface]] = {}
        self.char_walk_frames: dict[str, list[pygame.Surface]] = {}
        self.podium_image: pygame.Surface | None = None
        self.countdown_overlay: pygame.Surface | None = None

        self.menu_background: pygame.Surface | None = None
        self.shared_renderer = FighterRenderer()

        self._preload_character_select_assets()
        self._load_menu_background()
        self._rebuild_countdown_overlay()

    def _preload_character_select_assets(self) -> None:
        self._load_podium_image()
        self._load_idle_frames_only()
        self._load_walk_frames_only()

    def _load_podium_image(self) -> None:
        path = os.path.join("assets", "ui", "character_podium.png")
        if not os.path.exists(path):
            self.podium_image = None
            return

        try:
            self.podium_image = pygame.image.load(path).convert_alpha()
        except pygame.error:
            self.podium_image = None

    def _load_idle_frames_only(self) -> None:
        renderer = self.shared_renderer
        for char_name in self.CHAR_OPTIONS:
            sprite_set = renderer.sprite_sets.get(char_name, {})
            self.char_select_frames[char_name] = sprite_set.get("idle", [])

    def _load_walk_frames_only(self) -> None:
        renderer = self.shared_renderer
        for char_name in self.CHAR_OPTIONS:
            sprite_set = renderer.sprite_sets.get(char_name, {})
            walk_frames = sprite_set.get("run", [])
            if not walk_frames:
                walk_frames = sprite_set.get("walk", [])
            if not walk_frames:
                walk_frames = sprite_set.get("idle", [])
            self.char_walk_frames[char_name] = walk_frames

    def _load_menu_background(self) -> None:
        candidates = [
            os.path.join("assets", "backgrounds", "temple_stage.png"),
            os.path.join("assets", "backgrounds", "temple_bg.png"),
            os.path.join("assets", "backgrounds", "temple_stage_bg.png"),
        ]

        for path in candidates:
            if not os.path.exists(path):
                continue
            try:
                self.menu_background = pygame.image.load(path).convert()
                return
            except pygame.error:
                continue

        self.menu_background = None

    def _get_idle_frames(self, character_id: str) -> list[pygame.Surface]:
        return self.char_select_frames.get(character_id, [])

    def _get_walk_frames(self, character_id: str) -> list[pygame.Surface]:
        return self.char_walk_frames.get(character_id, [])

    def _rebuild_countdown_overlay(self) -> None:
        self.countdown_overlay = pygame.Surface((self.SCREEN_W, self.SCREEN_H), pygame.SRCALPHA)
        self.countdown_overlay.fill((0, 0, 0, 80))

    def _draw_menu_background(self) -> None:
        if self.menu_background is not None:
            bg = pygame.transform.scale(self.menu_background, (self.SCREEN_W, self.SCREEN_H))
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill((18, 18, 28))

        overlay = pygame.Surface((self.SCREEN_W, self.SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 95))
        self.screen.blit(overlay, (0, 0))

    def _draw_panel(
        self,
        rect: pygame.Rect,
        *,
        fill: tuple[int, int, int, int] = (12, 18, 28, 210),
        border: tuple[int, int, int] = (170, 180, 205),
        border_width: int = 2,
        radius: int = 14,
    ) -> None:
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel, fill, panel.get_rect(), border_radius=radius)
        pygame.draw.rect(panel, border, panel.get_rect(), border_width, border_radius=radius)
        self.screen.blit(panel, rect.topleft)

    def _draw_menu_walkers(self) -> None:
        walkers = [
            ("brawler", 0.0, self.SCREEN_H - 88, 95.0),
            ("swordsman", 0.45, self.SCREEN_H - 92, 120.0),
            ("gunner", 0.9, self.SCREEN_H - 86, 105.0),
        ]

        for i, (char_name, time_offset, y, speed) in enumerate(walkers):
            frames = self._get_walk_frames(char_name)
            if not frames:
                continue

            frame_time = 0.12
            anim_t = self.menu_anim_time + time_offset
            frame_index = int(anim_t / frame_time) % len(frames)
            frame = frames[frame_index]

            sprite_h = 84
            sprite_w = int(frame.get_width() * (sprite_h / frame.get_height()))
            sprite = pygame.transform.smoothscale(frame, (sprite_w, sprite_h))

            travel_w = self.SCREEN_W + 300
            start_offset = i * 180
            x = int((anim_t * speed + start_offset) % travel_w) - 150

            shadow = pygame.Surface((sprite_w + 18, 18), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 90), shadow.get_rect())
            self.screen.blit(shadow, (x - 9, y + sprite_h - 2))

            self.screen.blit(sprite, (x, y))

    def read_input_p1(self, inp: InputState, events: list[pygame.event.Event]) -> None:
        inp.reset_frame_events()
        keys = pygame.key.get_pressed()

        inp.left = keys[pygame.K_a]
        inp.right = keys[pygame.K_d]
        inp.down = keys[pygame.K_s]
        inp.up = keys[pygame.K_w]

        inp.jump = keys[pygame.K_SPACE] or keys[pygame.K_w]
        inp.dodge = keys[pygame.K_LSHIFT]
        inp.attack = keys[pygame.K_j]
        inp.ultimate = keys[pygame.K_k]

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_w):
                    inp.jump_pressed = True
                if event.key == pygame.K_LSHIFT:
                    inp.dodge_pressed = True
                if event.key == pygame.K_j:
                    inp.attack_pressed = True
                if event.key == pygame.K_k:
                    inp.ultimate_pressed = True

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_SPACE, pygame.K_w):
                    inp.jump_released = True

    def read_input_p2(self, inp: InputState, events: list[pygame.event.Event]) -> None:
        inp.reset_frame_events()
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        inp.left = keys[pygame.K_LEFT]
        inp.right = keys[pygame.K_RIGHT]
        inp.down = keys[pygame.K_DOWN]
        inp.up = keys[pygame.K_UP]

        inp.jump = keys[pygame.K_RCTRL] or keys[pygame.K_KP0] or keys[pygame.K_UP]
        inp.dodge = keys[pygame.K_RSHIFT] or keys[pygame.K_KP1]

        inp.attack = mouse_buttons[0]
        inp.ultimate = mouse_buttons[2]

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RCTRL, pygame.K_KP0, pygame.K_UP):
                    inp.jump_pressed = True
                if event.key in (pygame.K_RSHIFT, pygame.K_KP1):
                    inp.dodge_pressed = True

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_RCTRL, pygame.K_KP0, pygame.K_UP):
                    inp.jump_released = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    inp.attack_pressed = True
                elif event.button == 3:
                    inp.ultimate_pressed = True

    def handle_global_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.VIDEORESIZE:
                self.SCREEN_W, self.SCREEN_H = event.w, event.h
                self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H), pygame.RESIZABLE)
                self._rebuild_countdown_overlay()

                if self.match is not None:
                    self.match.camera.screen_w = self.SCREEN_W
                    self.match.camera.screen_h = self.SCREEN_H

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    def handle_mode_select_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_1:
                self.vs_mode_type = "local"
                self.reset_to_character_select()
                self.scene = "character_select"
            elif event.key == pygame.K_2:
                self.start_training_match()
            elif event.key == pygame.K_3:
                self.vs_mode_type = "real"
                self.reset_to_character_select()
                self.scene = "character_select"

    def start_training_match(self) -> None:
        self.match = TrainingMatch(self.SCREEN_W, self.SCREEN_H)
        self.scene = "training"

    def draw_mode_select(self) -> None:
        self.menu_anim_time += 1 / self.FPS
        self._draw_menu_background()

        title_panel = pygame.Rect(self.SCREEN_W // 2 - 240, 72, 480, 88)
        subtitle_panel = pygame.Rect(self.SCREEN_W // 2 - 140, 170, 280, 42)
        menu_panel = pygame.Rect(self.SCREEN_W // 2 - 230, 238, 460, 240)
        guide_panel = pygame.Rect(18, self.SCREEN_H - 52, 160, 34)

        self._draw_panel(title_panel, fill=(10, 16, 26, 220), border=(255, 210, 120), border_width=3, radius=18)
        self._draw_panel(subtitle_panel, fill=(10, 16, 26, 210), border=(180, 190, 210), radius=12)
        self._draw_panel(menu_panel, fill=(12, 18, 28, 215), border=(150, 160, 190), radius=16)
        self._draw_panel(guide_panel, fill=(10, 14, 24, 215), border=(130, 140, 170), radius=10)

        title = self.big_font.render("BROHALLA", True, (245, 245, 245))
        subtitle = self.mid_font.render("SELECT MODE", True, (215, 215, 225))
        multi = self.big_font.render("1. DEBUG VS", True, (255, 180, 120))
        training = self.big_font.render("2. TRAINING", True, (120, 200, 255))
        versus = self.big_font.render("3. BRAWL", True, (150, 255, 170))
        guide = self.font.render("ESC: EXIT", True, (225, 225, 225))

        self.screen.blit(title, (title_panel.centerx - title.get_width() // 2, title_panel.y + 24))
        self.screen.blit(subtitle, (subtitle_panel.centerx - subtitle.get_width() // 2, subtitle_panel.y + 11))

        self.screen.blit(multi, (menu_panel.centerx - multi.get_width() // 2, menu_panel.y + 34))
        self.screen.blit(training, (menu_panel.centerx - training.get_width() // 2, menu_panel.y + 104))
        self.screen.blit(versus, (menu_panel.centerx - versus.get_width() // 2, menu_panel.y + 174))
        self.screen.blit(guide, (guide_panel.x + 18, guide_panel.y + 9))

        self._draw_menu_walkers()

        pygame.display.flip()

    def handle_character_select_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if not self.p1_locked:
                    if event.key == pygame.K_a:
                        self.p1_choice_index = (self.p1_choice_index - 1) % len(self.CHAR_OPTIONS)
                    elif event.key == pygame.K_d:
                        self.p1_choice_index = (self.p1_choice_index + 1) % len(self.CHAR_OPTIONS)
                    elif event.key == pygame.K_j:
                        self.p1_locked = True

                if not self.p2_locked:
                    if event.key == pygame.K_LEFT:
                        self.p2_choice_index = (self.p2_choice_index - 1) % len(self.CHAR_OPTIONS)
                    elif event.key == pygame.K_RIGHT:
                        self.p2_choice_index = (self.p2_choice_index + 1) % len(self.CHAR_OPTIONS)
                    elif event.key == pygame.K_k:
                        self.p2_locked = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3 and not self.p2_locked:
                    self.p2_locked = True

        if self.p1_locked and self.p2_locked:
            if self.vs_mode_type == "real":
                self.start_real_vs_match()
            else:
                self.start_local_vs_match()

    def _draw_large_podium_preview(
        self,
        surface: pygame.Surface,
        *,
        center_x: int,
        char_name: str,
        player_label: str,
        player_color: tuple[int, int, int],
        locked: bool,
    ) -> None:
        podium_w = 330
        podium_h = 520

        preview_bottom_anchor = self.SCREEN_H + 180
        podium_x = center_x - podium_w // 2
        podium_y = preview_bottom_anchor - podium_h

        if self.podium_image is not None:
            podium = pygame.transform.smoothscale(self.podium_image, (podium_w, podium_h))
            surface.blit(podium, (podium_x, podium_y))
        else:
            rect = pygame.Rect(podium_x, podium_y, podium_w, podium_h)
            pygame.draw.rect(surface, (90, 100, 130), rect, border_radius=20)
            pygame.draw.rect(surface, (150, 170, 220), rect, 4, border_radius=20)

        frames = self._get_idle_frames(char_name)
        if frames:
            frame_time = 0.18
            frame_index = int(self.char_select_anim_time / frame_time) % len(frames)
            frame = frames[frame_index]

            sprite_h = 240
            sprite_w = int(frame.get_width() * (sprite_h / frame.get_height()))
            sprite = pygame.transform.smoothscale(frame, (sprite_w, sprite_h))

            sprite_x = center_x - sprite_w // 2
            sprite_y = podium_y - 210
            surface.blit(sprite, (sprite_x, sprite_y))

        label_panel = pygame.Rect(center_x - 54, self.SCREEN_H - 295, 108, 34)
        name_panel = pygame.Rect(center_x - 82, self.SCREEN_H - 258, 164, 32)

        panel_surf = pygame.Surface((label_panel.width, label_panel.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (*player_color, 60), panel_surf.get_rect(), border_radius=10)
        surface.blit(panel_surf, label_panel.topleft)

        name_surf_bg = pygame.Surface((name_panel.width, name_panel.height), pygame.SRCALPHA)
        pygame.draw.rect(name_surf_bg, (10, 16, 24, 180), name_surf_bg.get_rect(), border_radius=10)
        surface.blit(name_surf_bg, name_panel.topleft)

        label = self.big_font.render(player_label, True, player_color)
        surface.blit(label, (center_x - label.get_width() // 2, self.SCREEN_H - 290))

        name = self.mid_font.render(char_name.upper(), True, (245, 245, 245))
        surface.blit(name, (center_x - name.get_width() // 2, self.SCREEN_H - 255))

        state_text = "LOCKED" if locked else "SELECTING"
        state_color = (255, 220, 120) if locked else (210, 210, 210)
        state_surf = self.font.render(state_text, True, state_color)
        surface.blit(state_surf, (center_x - state_surf.get_width() // 2, self.SCREEN_H - 225))

    def _draw_character_cards(self, surface: pygame.Surface) -> None:
        card_w = 120
        card_h = 140
        gap = 34
        total_w = len(self.CHAR_OPTIONS) * card_w + (len(self.CHAR_OPTIONS) - 1) * gap
        start_x = self.SCREEN_W // 2 - total_w // 2
        card_y = 140

        panel_rect = pygame.Rect(start_x - 20, card_y - 18, total_w + 40, card_h + 36)
        self._draw_panel(panel_rect, fill=(12, 18, 28, 205), border=(150, 160, 190), radius=16)

        for i, char_name in enumerate(self.CHAR_OPTIONS):
            x = start_x + i * (card_w + gap)
            rect = pygame.Rect(x, card_y, card_w, card_h)

            pygame.draw.rect(surface, (46, 46, 62), rect, border_radius=12)

            if i == self.p1_choice_index:
                pygame.draw.rect(surface, (120, 200, 255), rect, 3, border_radius=12)

            if i == self.p2_choice_index:
                inner = rect.inflate(-8, -8)
                pygame.draw.rect(surface, (255, 180, 120), inner, 3, border_radius=12)

            frames = self._get_idle_frames(char_name)
            if frames:
                frame_time = 0.18
                frame_index = int(self.char_select_anim_time / frame_time) % len(frames)
                frame = frames[frame_index]

                sprite_h = 72
                sprite_w = int(frame.get_width() * (sprite_h / frame.get_height()))
                sprite = pygame.transform.smoothscale(frame, (sprite_w, sprite_h))

                sprite_x = x + card_w // 2 - sprite_w // 2
                sprite_y = card_y + 18
                surface.blit(sprite, (sprite_x, sprite_y))

            name = self.font.render(char_name.upper(), True, (240, 240, 240))
            surface.blit(name, (x + card_w // 2 - name.get_width() // 2, card_y + 100))

            if i == self.p1_choice_index:
                p1_mark = self.font.render("P1", True, (120, 200, 255))
                surface.blit(p1_mark, (x + 10, card_y + 8))

            if i == self.p2_choice_index:
                p2_mark = self.font.render("P2", True, (255, 180, 120))
                surface.blit(p2_mark, (x + card_w - p2_mark.get_width() - 10, card_y + 8))

    def update_match_countdown(self, dt: float) -> None:
        if not self.match_countdown_active:
            return

        self.match_countdown_timer += dt

        if self.match_countdown_timer >= self.match_countdown_duration:
            self.match_countdown_active = False

    def get_countdown_text(self) -> str | None:
        if not self.match_countdown_active:
            return None

        opening_text = getattr(self.match, "opening_text", None)
        t = self.match_countdown_timer

        if opening_text == "BRAWL!":
            if t < 1.2:
                return "BRAWL!"
            return None

        if t < 1.0:
            return "3"
        elif t < 2.0:
            return "2"
        elif t < 3.0:
            return "1"
        elif t < 4.0:
            return "BRAWL!"
        return None

    def draw_match_countdown_overlay(self) -> None:
        text = self.get_countdown_text()
        if text is None:
            return

        if self.countdown_overlay is not None:
            self.screen.blit(self.countdown_overlay, (0, 0))

        if text == "BRAWL!":
            color = (255, 200, 80)
            shadow_color = (40, 20, 10)
            surf = self.countdown_font.render(text, True, color)
            shadow = self.countdown_font.render(text, True, shadow_color)

            x = self.SCREEN_W // 2 - surf.get_width() // 2
            y = self.SCREEN_H // 2 - surf.get_height() // 2

            self.screen.blit(shadow, (x + 4, y + 4))
            self.screen.blit(surf, (x, y))
            return

        color = (255, 240, 120)
        surf = self.big_font.render(text, True, color)

        self.screen.blit(
            surf,
            (
                self.SCREEN_W // 2 - surf.get_width() // 2,
                self.SCREEN_H // 2 - surf.get_height() // 2,
            ),
        )

    def start_local_vs_match(self) -> None:
        p1_char = self.CHAR_OPTIONS[self.p1_choice_index]
        p2_char = self.CHAR_OPTIONS[self.p2_choice_index]

        self.match = LocalVsMatch(self.SCREEN_W, self.SCREEN_H, p1_char, p2_char)
        self.scene = "match"
        self.match_countdown_active = True
        self.match_countdown_timer = 0.0
        self.match_countdown_duration = 4.0

        self.match.camera.zoom = 1.55
        self.match.camera.target_zoom = 1.55

        center_x = self.match.stage.world_w / 2
        center_y = self.match.stage.world_h / 2

        visible_w = self.SCREEN_W / self.match.camera.zoom
        visible_h = self.SCREEN_H / self.match.camera.zoom

        self.match.camera.x = center_x - visible_w / 2
        self.match.camera.y = (center_y - 40) - visible_h / 2
        self.match.camera.clamp_to_world()

    def start_real_vs_match(self) -> None:
        p1_char = self.CHAR_OPTIONS[self.p1_choice_index]
        p2_char = self.CHAR_OPTIONS[self.p2_choice_index]

        self.match = RealVsMatch(self.SCREEN_W, self.SCREEN_H, p1_char, p2_char)
        self.scene = "match"
        self.match_countdown_active = True
        self.match_countdown_timer = 0.0
        self.match_countdown_duration = 4.0

        self.match.camera.zoom = 1.55
        self.match.camera.target_zoom = 1.55

        center_x = self.match.stage.world_w / 2
        center_y = self.match.stage.world_h / 2

        visible_w = self.SCREEN_W / self.match.camera.zoom
        visible_h = self.SCREEN_H / self.match.camera.zoom

        self.match.camera.x = center_x - visible_w / 2
        self.match.camera.y = (center_y - 40) - visible_h / 2
        self.match.camera.clamp_to_world()

    def reset_to_character_select(self) -> None:
        self.match = None
        self.p1_choice_index = 0
        self.p2_choice_index = 1
        self.p1_locked = False
        self.p2_locked = False
        self.char_select_anim_time = 0.0
        self.match_countdown_active = False
        self.match_countdown_timer = 0.0
        self.match_countdown_duration = 4.0

    def draw_character_select(self) -> None:
        self._draw_menu_background()
        self.char_select_anim_time += 1 / self.FPS

        title_panel = pygame.Rect(self.SCREEN_W // 2 - 240, 20, 480, 54)
        guide_panel = pygame.Rect(28, 78, 280, 68)
        mode_panel = pygame.Rect(28, 152, 180, 34)
        hint_panel = pygame.Rect(self.SCREEN_W // 2 - 145, 300, 290, 36)

        self._draw_panel(title_panel, fill=(12, 18, 28, 215), border=(220, 220, 230), radius=14)
        self._draw_panel(guide_panel, fill=(12, 18, 28, 210), border=(140, 160, 190), radius=12)
        self._draw_panel(mode_panel, fill=(12, 18, 28, 210), border=(150, 160, 185), radius=10)
        self._draw_panel(hint_panel, fill=(12, 18, 28, 205), border=(150, 160, 185), radius=10)

        title = self.big_font.render("CHARACTER SELECT", True, (240, 240, 240))
        self.screen.blit(title, (title_panel.centerx - title.get_width() // 2, title_panel.y + 14))

        guide1 = self.font.render("P1: A / D Move   J Confirm", True, (120, 200, 255))
        guide2 = self.font.render("P2: ← / → Move   K Confirm", True, (255, 180, 120))
        self.screen.blit(guide1, (guide_panel.x + 14, guide_panel.y + 17))
        self.screen.blit(guide2, (guide_panel.x + 14, guide_panel.y + 40))

        mode_text = "MODE: BRAWL" if self.vs_mode_type == "real" else "MODE: DEBUG VS"
        mode_color = (180, 255, 180) if self.vs_mode_type == "real" else (255, 200, 140)
        mode_surf = self.font.render(mode_text, True, mode_color)
        self.screen.blit(mode_surf, (mode_panel.x + 12, mode_panel.y + 9))

        self._draw_character_cards(self.screen)

        preview_p1_idx = self.p1_choice_index
        preview_p2_idx = self.p2_choice_index

        self._draw_large_podium_preview(
            self.screen,
            center_x=self.SCREEN_W // 4,
            char_name=self.CHAR_OPTIONS[preview_p1_idx],
            player_label="P1",
            player_color=(120, 200, 255),
            locked=self.p1_locked,
        )

        self._draw_large_podium_preview(
            self.screen,
            center_x=self.SCREEN_W * 3 // 4,
            char_name=self.CHAR_OPTIONS[preview_p2_idx],
            player_label="P2",
            player_color=(255, 180, 120),
            locked=self.p2_locked,
        )

        if self.p1_locked:
            lock_rect_1 = pygame.Rect(self.SCREEN_W // 4 - 72, self.SCREEN_H - 202, 144, 28)
            self._draw_panel(lock_rect_1, fill=(14, 20, 28, 220), border=(120, 200, 255), radius=10)
            locked1 = self.font.render("P1 LOCKED", True, (120, 200, 255))
            self.screen.blit(locked1, (lock_rect_1.centerx - locked1.get_width() // 2, lock_rect_1.y + 7))

        if self.p2_locked:
            lock_rect_2 = pygame.Rect(self.SCREEN_W * 3 // 4 - 72, self.SCREEN_H - 202, 144, 28)
            self._draw_panel(lock_rect_2, fill=(14, 20, 28, 220), border=(255, 180, 120), radius=10)
            locked2 = self.font.render("P2 LOCKED", True, (255, 180, 120))
            self.screen.blit(locked2, (lock_rect_2.centerx - locked2.get_width() // 2, lock_rect_2.y + 7))

        hint = self.font.render("SELECT YOUR CHARACTER", True, (220, 220, 220))
        self.screen.blit(hint, (hint_panel.centerx - hint.get_width() // 2, hint_panel.y + 10))

        pygame.display.flip()

    def handle_match_events(self, events: list[pygame.event.Event]) -> None:
        if self.match is None:
            return

        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_BACKQUOTE:
                self.return_to_menu()

            if event.key == pygame.K_F1 and getattr(self.match, "allow_debug_toggle", True):
                self.match.show_hud = not self.match.show_hud

            if event.key == pygame.K_r:
                self.scene = "mode_select"
                self.match = None
                self.reset_to_character_select()

    def return_to_menu(self) -> None:
        self.scene = "mode_select"
        self.match = None
        self.reset_to_character_select()

    def update_match(self, dt: float, events: list[pygame.event.Event]) -> None:
        if self.match is None:
            return

        if self.match_countdown_active:
            self.update_match_countdown(dt)

            center_x = self.match.stage.world_w / 2
            center_y = self.match.stage.world_h / 2

            self.match.camera.zoom = 1.55
            self.match.camera.target_zoom = 1.55

            visible_w = self.SCREEN_W / self.match.camera.zoom
            visible_h = self.SCREEN_H / self.match.camera.zoom

            self.match.camera.x = center_x - visible_w / 2
            self.match.camera.y = (center_y - 40) - visible_h / 2
            self.match.camera.clamp_to_world()
            return

        self.read_input_p1(self.match.player1.input, events)
        self.read_input_p2(self.match.player2.input, events)

        self.match.update(dt)

        if self.match.is_match_over:
            self.scene = "result"

    def handle_training_events(self, events: list[pygame.event.Event]) -> None:
        if self.match is None:
            return

        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_BACKQUOTE:
                self.return_to_menu()

            if event.key == pygame.K_F1:
                self.match.show_hud = not self.match.show_hud

            if event.key == pygame.K_r:
                self.match.reset()

            if event.key == pygame.K_1:
                self.match.set_player_character("brawler")
            if event.key == pygame.K_2:
                self.match.set_player_character("swordsman")
            if event.key == pygame.K_3:
                self.match.set_player_character("gunner")

            if event.key == pygame.K_TAB:
                self.scene = "mode_select"
                self.match = None
                self.reset_to_character_select()

    def update_training(self, dt: float, events: list[pygame.event.Event]) -> None:
        if self.match is None:
            return

        self.read_input_p1(self.match.player.input, events)
        self.match.update(dt)

    def handle_result_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_r:
                self.scene = "mode_select"
                self.match = None
                self.reset_to_character_select()

    def draw_result(self) -> None:
        self._draw_menu_background()

        if self.match is not None and self.match.winner is not None:
            winner_text = f"P{self.match.winner.player_index} WIN!"
        else:
            winner_text = "MATCH END"

        result_panel = pygame.Rect(self.SCREEN_W // 2 - 260, self.SCREEN_H // 2 - 90, 520, 170)
        self._draw_panel(result_panel, fill=(12, 18, 28, 220), border=(255, 220, 120), border_width=3, radius=18)

        title = self.big_font.render(winner_text, True, (255, 240, 120))
        info = self.font.render("R: Return To Menu", True, (230, 230, 230))

        self.screen.blit(title, (result_panel.centerx - title.get_width() // 2, result_panel.y + 50))
        self.screen.blit(info, (result_panel.centerx - info.get_width() // 2, result_panel.y + 105))

        pygame.display.flip()

    def run(self) -> None:
        while True:
            dt = self.clock.tick(self.FPS) / 1000.0
            dt = min(dt, 0.05)

            events = pygame.event.get()
            self.handle_global_events(events)

            if self.scene == "mode_select":
                self.handle_mode_select_events(events)
                self.draw_mode_select()

            elif self.scene == "character_select":
                self.handle_character_select_events(events)
                self.draw_character_select()

            elif self.scene == "match":
                self.handle_match_events(events)
                self.update_match(dt, events)
                if self.match is not None:
                    self.match.draw(self.screen, dt, self.font, draw_debug_hud)

                    if self.match_countdown_active:
                        self.draw_match_countdown_overlay()

                    pygame.display.flip()

            elif self.scene == "training":
                self.handle_training_events(events)
                self.update_training(dt, events)
                if self.match is not None:
                    self.match.draw(self.screen, dt, self.font, draw_debug_hud)
                    pygame.display.flip()

            elif self.scene == "result":
                self.handle_result_events(events)
                self.draw_result()
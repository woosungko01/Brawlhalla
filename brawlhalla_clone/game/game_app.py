# game/game_app.py

import os
import sys
import pygame

from core.input_state import InputState
from game.training_match import TrainingMatch
from game.local_vs_match import LocalVsMatch
from utils.debug_hud import draw_debug_hud
from rendering.fighter_renderer import FighterRenderer


class GameApp:
    FPS = 60
    TITLE = "Brawlhalla OOP Prototype"

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
        self.big_font = pygame.font.SysFont("monospace", 26)

        self.scene = "mode_select"
        self.match = None

        self.match_countdown_active = False
        self.match_countdown_timer = 0.0
        self.match_countdown_duration = 4.0

        self.p1_choice_index = 0
        self.p2_choice_index = 1
        self.p1_locked = False
        self.p2_locked = False

        self.char_select_anim_time = 0.0

        self.char_select_frames: dict[str, list[pygame.Surface]] = {}
        self.podium_image: pygame.Surface | None = None

        self._preload_character_select_assets()

    def _preload_character_select_assets(self) -> None:
        self._load_podium_image()
        self._load_idle_frames_only()

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
        renderer = FighterRenderer()
        for char_name in self.CHAR_OPTIONS:
            sprite_set = renderer.sprite_sets.get(char_name, {})
            self.char_select_frames[char_name] = sprite_set.get("idle", [])

    def _get_idle_frames(self, character_id: str) -> list[pygame.Surface]:
        return self.char_select_frames.get(character_id, [])

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

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    def handle_mode_select_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_1:
                self.reset_to_character_select()
                self.scene = "character_select"
            elif event.key == pygame.K_2:
                self.start_training_match()

    def start_training_match(self) -> None:
        self.match = TrainingMatch(self.SCREEN_W, self.SCREEN_H)
        self.scene = "training"

    def draw_mode_select(self) -> None:
        self.screen.fill((18, 18, 28))

        title = self.big_font.render("SELECT MODE", True, (240, 240, 240))
        multi = self.big_font.render("1. MULTI", True, (255, 180, 120))
        training = self.big_font.render("2. TRAINING", True, (120, 200, 255))
        guide = self.font.render("ESC: 종료", True, (180, 180, 180))

        self.screen.blit(title, (self.SCREEN_W // 2 - title.get_width() // 2, 120))
        self.screen.blit(multi, (self.SCREEN_W // 2 - multi.get_width() // 2, 260))
        self.screen.blit(training, (self.SCREEN_W // 2 - training.get_width() // 2, 330))
        self.screen.blit(guide, (20, self.SCREEN_H - 30))

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

        # 화면 아래로 내림
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
        card_y = 120

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

        t = self.match_countdown_timer

        if t < 1.0:
            return "3"
        elif t < 2.0:
            return "2"
        elif t < 3.0:
            return "1"
        elif t < 4.0:
            return "GO!"
        return None

    def draw_match_countdown_overlay(self) -> None:
        text = self.get_countdown_text()
        if text is None:
            return

        # 반투명 어둡게
        overlay = pygame.Surface((self.SCREEN_W, self.SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 90))
        self.screen.blit(overlay, (0, 0))

        color = (255, 240, 120) if text != "GO!" else (120, 255, 140)
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

        # 카메라를 즉시 맵 중앙으로 세팅
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

    def draw_character_select(self) -> None:
        self.screen.fill((18, 18, 28))
        self.char_select_anim_time += 1 / self.FPS

        title = self.big_font.render("CHARACTER SELECT", True, (240, 240, 240))
        self.screen.blit(title, (self.SCREEN_W // 2 - title.get_width() // 2, 28))

        guide1 = self.font.render("P1: A / D 이동   J 확정", True, (120, 200, 255))
        guide2 = self.font.render("P2: ← / → 이동   K 확정", True, (255, 180, 120))
        self.screen.blit(guide1, (40, 72))
        self.screen.blit(guide2, (40, 95))

        self._draw_character_cards(self.screen)

        # 핵심: 미리보기는 hover가 아니라 현재 선택 인덱스
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
            locked1 = self.font.render("P1 LOCKED", True, (120, 200, 255))
            self.screen.blit(locked1, (self.SCREEN_W // 4 - locked1.get_width() // 2, self.SCREEN_H - 195))

        if self.p2_locked:
            locked2 = self.font.render("P2 LOCKED", True, (255, 180, 120))
            self.screen.blit(locked2, (self.SCREEN_W * 3 // 4 - locked2.get_width() // 2, self.SCREEN_H - 195))

        hint = self.font.render("SELECT YOUR CHARACTER", True, (200, 200, 200))
        self.screen.blit(hint, (self.SCREEN_W // 2 - hint.get_width() // 2, 280))

        pygame.display.flip()

    def handle_match_events(self, events: list[pygame.event.Event]) -> None:
        if self.match is None:
            return

        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_F1:
                self.match.show_hud = not self.match.show_hud

            if event.key == pygame.K_r:
                self.scene = "mode_select"
                self.match = None
                self.reset_to_character_select()

    def update_match(self, dt: float, events: list[pygame.event.Event]) -> None:
        if self.match is None:
            return

        if self.match_countdown_active:
            self.update_match_countdown(dt)

            # countdown 동안 카메라를 맵 중앙으로 유지
            center_x = self.match.stage.world_w / 2
            center_y = self.match.stage.world_h / 2
            self.match.camera.update(center_x, center_y)

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
        self.screen.fill((15, 15, 25))

        if self.match is not None and self.match.winner is not None:
            winner_text = f"P{self.match.winner.player_index} WIN!"
        else:
            winner_text = "MATCH END"

        title = self.big_font.render(winner_text, True, (255, 240, 120))
        info = self.font.render("R: 모드 선택 화면으로 돌아가기", True, (220, 220, 220))

        self.screen.blit(title, (self.SCREEN_W // 2 - title.get_width() // 2, self.SCREEN_H // 2 - 40))
        self.screen.blit(info, (self.SCREEN_W // 2 - info.get_width() // 2, self.SCREEN_H // 2 + 10))

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

            elif self.scene == "result":
                self.handle_result_events(events)
                self.draw_result()
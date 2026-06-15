# game/game_app.py
# 게임 최상위 앱 파일
# - 캐릭터 선택 화면
# - 로컬 2인 대전 시작
# - 결과 화면
# - 1P / 2P 입력 처리

import sys
import pygame

from core.input_state import InputState
from game.training_match import TrainingMatch
from game.local_vs_match import LocalVsMatch
from utils.debug_hud import draw_debug_hud


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
        self.big_font = pygame.font.SysFont("monospace", 26)

        # scene: "character_select" | "match" | "result" | "training"
        self.scene = "character_select"

        self.match = None

        # 캐릭터 선택 상태
        self.p1_choice_index = 0
        self.p2_choice_index = 1
        self.p1_locked = False
        self.p2_locked = False

    # ─────────────────────────────────────────────────────
    # 입력 처리
    # ─────────────────────────────────────────────────────

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

        # 위 화살표도 점프 버튼으로 취급
        inp.jump = keys[pygame.K_RCTRL] or keys[pygame.K_KP0] or keys[pygame.K_UP]
        inp.dodge = keys[pygame.K_RSHIFT] or keys[pygame.K_KP1]

        inp.attack = mouse_buttons[0]  # 좌클릭
        inp.ultimate = mouse_buttons[2]  # 우클릭

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
    # ─────────────────────────────────────────────────────
    # Scene 전역 이벤트
    # ─────────────────────────────────────────────────────

    def handle_global_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    # ─────────────────────────────────────────────────────
    # 캐릭터 선택 화면
    # ─────────────────────────────────────────────────────

    def handle_character_select_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            # 1P 선택: A/D 이동, J 확정
            if not self.p1_locked and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.p1_choice_index = (self.p1_choice_index - 1) % len(self.CHAR_OPTIONS)
                elif event.key == pygame.K_d:
                    self.p1_choice_index = (self.p1_choice_index + 1) % len(self.CHAR_OPTIONS)
                elif event.key == pygame.K_j:
                    self.p1_locked = True

            # 2P 선택: 좌/우 이동, 우클릭 확정
            if not self.p2_locked:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.p2_choice_index = (self.p2_choice_index - 1) % len(self.CHAR_OPTIONS)
                    elif event.key == pygame.K_RIGHT:
                        self.p2_choice_index = (self.p2_choice_index + 1) % len(self.CHAR_OPTIONS)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:  # 우클릭
                        self.p2_locked = True

            # 둘 다 선택 완료 → match 시작
            if self.p1_locked and self.p2_locked:
                self.start_local_vs_match()

    def start_local_vs_match(self) -> None:
        p1_char = self.CHAR_OPTIONS[self.p1_choice_index]
        p2_char = self.CHAR_OPTIONS[self.p2_choice_index]

        self.match = LocalVsMatch(self.SCREEN_W, self.SCREEN_H, p1_char, p2_char)
        self.scene = "match"

    def reset_to_character_select(self) -> None:
        self.scene = "character_select"
        self.match = None
        self.p1_choice_index = 0
        self.p2_choice_index = 1
        self.p1_locked = False
        self.p2_locked = False

    def draw_character_select(self) -> None:
        self.screen.fill((20, 20, 30))

        title = self.big_font.render("CHARACTER SELECT", True, (240, 240, 240))
        self.screen.blit(title, (self.SCREEN_W // 2 - title.get_width() // 2, 60))

        p1_title = self.font.render("P1  A/D: 선택   J: 확정", True, (120, 200, 255))
        p2_title = self.font.render("P2  ←/→: 선택   Num2: 확정", True, (255, 180, 120))

        self.screen.blit(p1_title, (120, 140))
        self.screen.blit(p2_title, (self.SCREEN_W - 360, 140))

        box_y = 250
        spacing = 220

        for i, char_name in enumerate(self.CHAR_OPTIONS):
            x = self.SCREEN_W // 2 - spacing + i * spacing

            base_rect = pygame.Rect(x - 70, box_y - 40, 140, 140)

            # P1 선택 강조
            p1_color = (60, 120, 180) if i == self.p1_choice_index else (45, 45, 60)
            pygame.draw.rect(self.screen, p1_color, base_rect, border_radius=10)
            pygame.draw.rect(self.screen, (120, 200, 255), base_rect, 3, border_radius=10)

            # P2 선택 강조 (살짝 아래에 테두리 추가 느낌)
            p2_rect = pygame.Rect(x - 66, box_y - 36, 132, 132)
            if i == self.p2_choice_index:
                pygame.draw.rect(self.screen, (255, 180, 120), p2_rect, 3, border_radius=10)

            label = self.big_font.render(char_name.upper(), True, (240, 240, 240))
            self.screen.blit(label, (x - label.get_width() // 2, box_y + 10))

            if i == self.p1_choice_index:
                p1_mark = self.font.render("P1", True, (120, 200, 255))
                self.screen.blit(p1_mark, (x - p1_mark.get_width() // 2, box_y - 28))

            if i == self.p2_choice_index:
                p2_mark = self.font.render("P2", True, (255, 180, 120))
                self.screen.blit(p2_mark, (x - p2_mark.get_width() // 2, box_y + 68))

        if self.p1_locked:
            locked1 = self.font.render("P1 LOCKED", True, (120, 200, 255))
            self.screen.blit(locked1, (120, 190))

        if self.p2_locked:
            locked2 = self.font.render("P2 LOCKED", True, (255, 180, 120))
            self.screen.blit(locked2, (self.SCREEN_W - 220, 190))

        guide = self.font.render("ESC: 종료", True, (180, 180, 180))
        self.screen.blit(guide, (20, self.SCREEN_H - 30))

        pygame.display.flip()

    # ─────────────────────────────────────────────────────
    # 매치 화면
    # ─────────────────────────────────────────────────────

    def handle_match_events(self, events: list[pygame.event.Event]) -> None:
        if self.match is None:
            return

        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_F1:
                self.match.show_hud = not self.match.show_hud

            if event.key == pygame.K_r:
                # 결과 화면으로 안 가고 바로 선택 화면으로 되돌림
                self.reset_to_character_select()

    def update_match(self, dt: float, events: list[pygame.event.Event]) -> None:
        if self.match is None:
            return

        self.read_input_p1(self.match.player1.input, events)
        self.read_input_p2(self.match.player2.input, events)

        self.match.update(dt)

        if self.match.is_match_over:
            self.scene = "result"

    # ─────────────────────────────────────────────────────
    # 결과 화면
    # ─────────────────────────────────────────────────────

    def handle_result_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_r:
                self.reset_to_character_select()

    def draw_result(self) -> None:
        self.screen.fill((15, 15, 25))

        if self.match is not None and self.match.winner is not None:
            winner_text = f"P{self.match.winner.player_index} WIN!"
        else:
            winner_text = "MATCH END"

        title = self.big_font.render(winner_text, True, (255, 240, 120))
        info = self.font.render("R: 캐릭터 선택 화면으로 돌아가기", True, (220, 220, 220))

        self.screen.blit(title, (self.SCREEN_W // 2 - title.get_width() // 2, self.SCREEN_H // 2 - 40))
        self.screen.blit(info, (self.SCREEN_W // 2 - info.get_width() // 2, self.SCREEN_H // 2 + 10))

        pygame.display.flip()

    # ─────────────────────────────────────────────────────
    # 메인 루프
    # ─────────────────────────────────────────────────────

    def run(self) -> None:
        while True:
            dt = self.clock.tick(self.FPS) / 1000.0
            dt = min(dt, 0.05)

            events = pygame.event.get()
            self.handle_global_events(events)

            if self.scene == "character_select":
                self.handle_character_select_events(events)
                self.draw_character_select()

            elif self.scene == "match":
                self.handle_match_events(events)
                self.update_match(dt, events)
                if self.match is not None:
                    self.match.draw(self.screen, dt, self.font, draw_debug_hud)

            elif self.scene == "result":
                self.handle_result_events(events)
                self.draw_result()
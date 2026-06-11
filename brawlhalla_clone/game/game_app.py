import sys
import pygame

from core.input_state import InputState
from game.training_match import TrainingMatch
from utils.debug_hud import draw_debug_hud


class GameApp:
    SCREEN_W = 1280
    SCREEN_H = 720
    FPS = 60
    TITLE = "Brawlhalla OOP Prototype"

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        pygame.display.set_caption(self.TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 13)

        self.match = TrainingMatch(self.SCREEN_W, self.SCREEN_H)

    def read_input(self, inp: InputState, events: list[pygame.event.Event]) -> None:
        inp.reset_frame_events()
        keys = pygame.key.get_pressed()

        inp.left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        inp.right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        inp.down = keys[pygame.K_s] or keys[pygame.K_DOWN]
        inp.up = keys[pygame.K_w] or keys[pygame.K_UP]

        inp.jump = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
        inp.dodge = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        inp.attack = keys[pygame.K_j]
        inp.ultimate = keys[pygame.K_k]

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    inp.jump_pressed = True
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    inp.dodge_pressed = True
                if event.key == pygame.K_j:
                    inp.attack_pressed = True
                if event.key == pygame.K_k:
                    inp.ultimate_pressed = True
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    inp.jump_released = True

    def handle_global_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
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

    def run(self) -> None:
        while True:
            dt = self.clock.tick(self.FPS) / 1000.0
            dt = min(dt, 0.05)

            events = pygame.event.get()
            self.handle_global_events(events)
            self.read_input(self.match.player.input, events)

            self.match.update(dt)
            self.match.draw(self.screen, self.font, draw_debug_hud)
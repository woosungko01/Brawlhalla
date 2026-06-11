# rendering/match_renderer.py

import pygame

from systems.fighter_combat import get_attack_hitbox


class MatchRenderer:
    BG_COLOR = (30, 30, 45)
    PLAYER_COLOR = (100, 180, 255)
    HARD_PLATFORM_COLOR = (80, 200, 120)
    HARD_PLATFORM_BORDER = (60, 160, 90)
    SOFT_PLATFORM_COLOR = (220, 190, 90)
    SOFT_PLATFORM_BORDER = (180, 145, 60)
    WORLD_BORDER_COLOR = (90, 90, 120)
    DUMMY_COLOR = (230, 120, 120)
    HITBOX_COLOR = (255, 220, 80)

    def draw(self, surface: pygame.Surface, match, font: pygame.font.Font, draw_debug_hud_fn) -> None:
        surface.fill(self.BG_COLOR)

        self._draw_world(surface, match)
        self._draw_platforms(surface, match)
        self._draw_fighters(surface, match)
        self._draw_player_eye(surface, match)
        self._draw_player_state(surface, match, font)
        self._draw_character_label(surface, match, font)
        self._draw_attack_hitbox(surface, match)
        self._draw_ultimate_label(surface, match, font)

        if match.show_hud:
            draw_debug_hud_fn(surface, match.player)

        pygame.display.flip()

    def _draw_world(self, surface: pygame.Surface, match) -> None:
        world_rect = pygame.Rect(
            int(-match.camera.x),
            int(-match.camera.y),
            match.stage.world_w,
            match.stage.world_h,
        )
        pygame.draw.rect(surface, self.WORLD_BORDER_COLOR, world_rect, 3)

    def _draw_platforms(self, surface: pygame.Surface, match) -> None:
        for plat in match.stage.platforms:
            rect = pygame.Rect(
                int(plat.x - match.camera.x),
                int(plat.y - match.camera.y),
                int(plat.width),
                int(plat.height),
            )

            if getattr(plat, "is_soft", False):
                pygame.draw.rect(surface, self.SOFT_PLATFORM_COLOR, rect)
                pygame.draw.rect(surface, self.SOFT_PLATFORM_BORDER, rect, 2)
            else:
                pygame.draw.rect(surface, self.HARD_PLATFORM_COLOR, rect)
                pygame.draw.rect(surface, self.HARD_PLATFORM_BORDER, rect, 2)

    def _draw_fighters(self, surface: pygame.Surface, match) -> None:
        for fighter, color, border in (
            (match.player, self.PLAYER_COLOR, (60, 140, 220)),
            (match.dummy, self.DUMMY_COLOR, (180, 80, 80)),
        ):
            rect = pygame.Rect(
                int(fighter.rect_x - match.camera.x),
                int(fighter.rect_y - match.camera.y),
                fighter.width,
                fighter.height,
            )
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, border, rect, 2)

    def _draw_player_eye(self, surface: pygame.Surface, match) -> None:
        eye_x = int(match.player.pos.x - match.camera.x + match.player.facing * 10)
        eye_y = int(match.player.rect_y - match.camera.y + 14)
        pygame.draw.circle(surface, (255, 255, 255), (eye_x, eye_y), 5)

    def _draw_player_state(self, surface: pygame.Surface, match, font: pygame.font.Font) -> None:
        state_surf = font.render(match.player.move_state, True, (200, 200, 200))
        surface.blit(
            state_surf,
            (
                int(match.player.pos.x - match.camera.x - state_surf.get_width() // 2),
                int(match.player.rect_y - match.camera.y - 22),
            ),
        )

    def _draw_character_label(self, surface: pygame.Surface, match, font: pygame.font.Font) -> None:
        char_surf = font.render(match.player.character.character_id, True, (255, 255, 255))
        surface.blit(char_surf, (20, 20))

    def _draw_attack_hitbox(self, surface: pygame.Surface, match) -> None:
        attack_hitbox = get_attack_hitbox(match.player)
        if attack_hitbox is None:
            return

        hb = pygame.Rect(
            int(attack_hitbox.x - match.camera.x),
            int(attack_hitbox.y - match.camera.y),
            attack_hitbox.width,
            attack_hitbox.height,
        )
        pygame.draw.rect(surface, self.HITBOX_COLOR, hb, 2)

    def _draw_ultimate_label(self, surface: pygame.Surface, match, font: pygame.font.Font) -> None:
        if match.player.ultimate_timer <= 0.0:
            return

        ult_surf = font.render("ULT ACTIVE", True, (255, 220, 120))
        surface.blit(ult_surf, (20, 60))
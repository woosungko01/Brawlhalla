# rendering/fighter_renderer.py

from __future__ import annotations
import pygame

from rendering.animation import AnimationClip, AnimationPlayer


class FighterRenderer:
    def __init__(self) -> None:
        self.players: dict[int, AnimationPlayer] = {}
        self.default_clips = {
            "idle": AnimationClip("idle", frame_count=4, frame_time=0.18, loop=True),
            "run": AnimationClip("run", frame_count=6, frame_time=0.08, loop=True),
            "airborne": AnimationClip("airborne", frame_count=2, frame_time=0.12, loop=True),
            "jump_startup": AnimationClip("jump_startup", frame_count=2, frame_time=0.05, loop=False),
            "wall_cling": AnimationClip("wall_cling", frame_count=2, frame_time=0.12, loop=True),
            "dashing": AnimationClip("dashing", frame_count=3, frame_time=0.04, loop=True),
            "dodge": AnimationClip("dodge", frame_count=3, frame_time=0.05, loop=False),
        }

    def update(self, fighter, dt: float) -> None:
        player = self._get_player(fighter)
        clip = self.default_clips.get(fighter.move_state, self.default_clips["idle"])
        player.play(clip)
        player.update(dt)

    def draw(self, surface: pygame.Surface, fighter, camera, base_color, border_color) -> None:
        player = self._get_player(fighter)

        rect = pygame.Rect(
            int(fighter.rect_x - camera.x),
            int(fighter.rect_y - camera.y),
            fighter.width,
            fighter.height,
        )

        fill_color = self._get_animated_color(base_color, player.frame_index, fighter)
        pygame.draw.rect(surface, fill_color, rect, border_radius=8)
        pygame.draw.rect(surface, border_color, rect, 2, border_radius=8)

        self._draw_face(surface, fighter, camera, player.frame_index)

    def _get_player(self, fighter) -> AnimationPlayer:
        key = id(fighter)
        if key not in self.players:
            self.players[key] = AnimationPlayer()
        return self.players[key]

    def _get_animated_color(self, base_color: tuple[int, int, int], frame: int, fighter) -> tuple[int, int, int]:
        r, g, b = base_color

        if fighter.invuln_timer > 0.0:
            flash = 40 if frame % 2 == 0 else 0
            return (
                min(255, r + flash),
                min(255, g + flash),
                min(255, b + flash),
            )

        if fighter.is_attacking:
            return (
                min(255, r + 20),
                min(255, g + 10),
                min(255, b + 10),
            )

        if fighter.move_state == "run":
            pulse = 8 if frame % 2 == 0 else 0
            return (r, min(255, g + pulse), min(255, b + pulse))

        return base_color

    def _draw_face(self, surface: pygame.Surface, fighter, camera, frame: int) -> None:
        eye_x = int(fighter.pos.x - camera.x + fighter.facing * 10)
        eye_y = int(fighter.rect_y - camera.y + 14 + (1 if frame % 2 == 0 and fighter.move_state == "run" else 0))
        pygame.draw.circle(surface, (255, 255, 255), (eye_x, eye_y), 5)
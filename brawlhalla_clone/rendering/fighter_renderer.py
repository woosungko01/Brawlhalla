from __future__ import annotations
import os
import pygame

from rendering.animation import AnimationClip, AnimationPlayer


class FighterRenderer:
    FRAME_W = 128
    FRAME_H = 128

    def __init__(self) -> None:
        self.players: dict[int, AnimationPlayer] = {}
        self.sprite_sets: dict[str, dict[str, list[pygame.Surface]]] = {}

        self.default_clips = {
            "idle": AnimationClip("idle", frame_count=4, frame_time=0.18, loop=True),
            "run": AnimationClip("run", frame_count=6, frame_time=0.08, loop=True),
            "airborne": AnimationClip("airborne", frame_count=2, frame_time=0.12, loop=True),
            "jump_startup": AnimationClip("jump_startup", frame_count=2, frame_time=0.05, loop=False),
            "wall_cling": AnimationClip("wall_cling", frame_count=2, frame_time=0.12, loop=True),
            "dashing": AnimationClip("dashing", frame_count=3, frame_time=0.04, loop=True),
            "dodge": AnimationClip("dodge", frame_count=3, frame_time=0.05, loop=False),
        }

        self._load_all_sprite_sets()

    def update(self, fighter, dt: float) -> None:
        player = self._get_player(fighter)
        clip = self._resolve_clip_for_fighter(fighter)
        player.play(clip)
        player.update(dt)

    def draw(self, surface: pygame.Surface, fighter, camera, base_color, border_color) -> None:
        player = self._get_player(fighter)

        frames = self._get_current_frames(fighter)
        if frames:
            self._draw_sprite(surface, fighter, camera, player, frames)
            return

        rect = pygame.Rect(
            int((fighter.rect_x - camera.x) * camera.zoom),
            int((fighter.rect_y - camera.y) * camera.zoom),
            int(fighter.width * camera.zoom),
            int(fighter.height * camera.zoom),
        )

        pygame.draw.rect(surface, base_color, rect, border_radius=8)
        pygame.draw.rect(surface, border_color, rect, max(1, int(2 * camera.zoom)), border_radius=8)

    def _get_player(self, fighter) -> AnimationPlayer:
        key = id(fighter)
        if key not in self.players:
            self.players[key] = AnimationPlayer()
        return self.players[key]

    def _resolve_clip_for_fighter(self, fighter) -> AnimationClip:
        anim_name, frame_count = self._resolve_animation_name_and_frames(fighter)

        if fighter.is_attacking:
            return AnimationClip(anim_name, frame_count=max(1, frame_count), frame_time=0.09, loop=True)

        if fighter.move_state == "run":
            return AnimationClip(anim_name, frame_count=max(1, frame_count), frame_time=0.09, loop=True)

        if fighter.move_state in ("airborne", "jump_startup", "wall_cling"):
            return AnimationClip(anim_name, frame_count=max(1, frame_count), frame_time=0.12, loop=True)

        if fighter.move_state in ("dashing", "dodge"):
            return AnimationClip(anim_name, frame_count=max(1, frame_count), frame_time=0.07, loop=True)

        return AnimationClip(anim_name, frame_count=max(1, frame_count), frame_time=0.14, loop=True)

    def _resolve_animation_name_and_frames(self, fighter) -> tuple[str, int]:
        sprite_set = self.sprite_sets.get(fighter.character.character_id, {})

        if fighter.is_attacking:
            attack_anim = self._map_attack_animation_name(fighter)
            if attack_anim is not None:
                frames = sprite_set.get(attack_anim)
                if frames:
                    return attack_anim, len(frames)

        if fighter.hitstun_timer > 0.0 or fighter.stun_timer > 0.0:
            frames = sprite_set.get("hurt")
            if frames:
                return "hurt", len(frames)

        if getattr(fighter, "is_dead", False):
            frames = sprite_set.get("dead")
            if frames:
                return "dead", len(frames)

        if fighter.move_state == "run":
            frames = sprite_set.get("run")
            if frames:
                return "run", len(frames)

        if fighter.move_state in ("airborne", "jump_startup", "wall_cling"):
            frames = sprite_set.get("jump")
            if frames:
                return "jump", len(frames)

        if fighter.move_state in ("dashing", "dodge"):
            frames = sprite_set.get("run")
            if frames:
                return "run", len(frames)

        frames = sprite_set.get("idle")
        if frames:
            return "idle", len(frames)

        clip = self.default_clips.get(fighter.move_state, self.default_clips["idle"])
        return clip.name, clip.frame_count

    def _map_attack_animation_name(self, fighter) -> str | None:
        attack_name = fighter.attack_name or ""

        mapping = {
            "neutral": "attack_neutral",
            "side": "attack_side",
            "up": "attack_up",
            "up_air": "attack_up",
            "down_ground": "attack_down",
            "down_air": "attack_down",
        }

        return mapping.get(attack_name)

    def _get_current_frames(self, fighter) -> list[pygame.Surface] | None:
        sprite_set = self.sprite_sets.get(fighter.character.character_id)
        if not sprite_set:
            return None

        anim_name, _ = self._resolve_animation_name_and_frames(fighter)
        frames = sprite_set.get(anim_name)
        if frames:
            return frames

        return None

    def _draw_sprite(
        self,
        surface: pygame.Surface,
        fighter,
        camera,
        player: AnimationPlayer,
        frames: list[pygame.Surface],
    ) -> None:
        if not frames:
            return

        frame = frames[player.frame_index % len(frames)]

        if fighter.facing < 0:
            frame = pygame.transform.flip(frame, True, False)

        target_h = int(fighter.height * camera.zoom * 1.9)
        target_w = int(self.FRAME_W * (target_h / self.FRAME_H))

        if target_w <= 0 or target_h <= 0:
            return

        scaled = pygame.transform.scale(frame, (target_w, target_h))

        center_sx, center_sy = camera.world_to_screen(fighter.pos.x, fighter.pos.y)
        draw_x = center_sx - target_w // 2
        draw_y = center_sy - int(target_h * 0.72)

        surface.blit(scaled, (draw_x, draw_y))

    def _load_all_sprite_sets(self) -> None:
        self.sprite_sets["brawler"] = self._load_character_sprite_set(
            folder_name="White_Werewolf",
            file_map={
                "idle": "Idle.png",
                "run": "Run.png",
                "jump": "Jump.png",
                "hurt": "Hurt.png",
                "dead": "Dead.png",
                "attack_neutral": "Attack_1.png",
                "attack_side": "Run+Attack.png",
                "attack_up": "Attack_2.png",
                "attack_down": "Attack_3.png",
            },
        )

        self.sprite_sets["swordsman"] = self._load_character_sprite_set(
            folder_name="Knight_1",
            file_map={
                "idle": "Idle.png",
                "run": "Run.png",
                "jump": "Jump.png",
                "hurt": "Hurt.png",
                "dead": "Dead.png",
                "attack_neutral": "Attack 1.png",
                "attack_side": "Run+Attack.png",
                "attack_up": "Attack 2.png",
                "attack_down": "Attack 3.png",
            },
        )

        self.sprite_sets["gunner"] = self._load_character_sprite_set(
            folder_name="Samurai_Archer",
            file_map={
                "idle": "Idle.png",
                "run": "Run.png",
                "jump": "Jump.png",
                "hurt": "Hurt.png",
                "dead": "Dead.png",
                "attack_neutral": "Attack_1.png",
                "attack_side": "Shot.png",
                "attack_up": "Attack_2.png",
                "attack_down": "Attack_3.png",
            },
        )

    def _load_character_sprite_set(self, folder_name: str, file_map: dict[str, str]) -> dict[str, list[pygame.Surface]]:
        result: dict[str, list[pygame.Surface]] = {}

        for anim_name, filename in file_map.items():
            path = os.path.join("assets", folder_name, filename)
            frames = self._load_sheet_frames(path)
            if frames:
                result[anim_name] = frames

        return result

    def _load_sheet_frames(self, path: str) -> list[pygame.Surface]:
        if not os.path.exists(path):
            return []

        try:
            sheet = pygame.image.load(path).convert_alpha()
        except pygame.error:
            return []

        width = sheet.get_width()
        height = sheet.get_height()

        if width < self.FRAME_W or height < self.FRAME_H:
            return []

        cols = width // self.FRAME_W
        rows = height // self.FRAME_H

        frames: list[pygame.Surface] = []

        for row in range(rows):
            for col in range(cols):
                x = col * self.FRAME_W
                y = row * self.FRAME_H

                if x + self.FRAME_W > width or y + self.FRAME_H > height:
                    continue

                frame = pygame.Surface((self.FRAME_W, self.FRAME_H), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), pygame.Rect(x, y, self.FRAME_W, self.FRAME_H))

                if self._is_blank_frame(frame):
                    continue

                frames.append(frame)

        return frames

    def _is_blank_frame(self, frame: pygame.Surface) -> bool:
        bbox = frame.get_bounding_rect(min_alpha=1)
        return bbox.width == 0 or bbox.height == 0
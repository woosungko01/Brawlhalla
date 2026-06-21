from __future__ import annotations
import os
import pygame

from rendering.animation import AnimationClip, AnimationPlayer


class FighterRenderer:
    #캐릭터의 애니메이션 및 외관 구현
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
            "wall_cling": AnimationClip("wall_cling", frame_count=1, frame_time=0.12, loop=True),
            "dashing": AnimationClip("dashing", frame_count=1, frame_time=0.04, loop=True),
            "dodge": AnimationClip("dodge", frame_count=1, frame_time=0.05, loop=True),
            "stun": AnimationClip("stun", frame_count=1, frame_time=0.10, loop=True),
        }

        self._load_all_sprite_sets()

    def update(self, fighter, dt: float) -> None:
        player = self._get_player(fighter)
        clip = self._resolve_clip_for_fighter(fighter)
        player.play(clip)
        player.update(dt)

    def draw(self, surface: pygame.Surface, fighter, camera, base_color, border_color) -> None:
        player = self._get_player(fighter)

        frame = self._get_current_frame_surface(fighter, player)
        if frame is not None:
            self._draw_sprite(surface, fighter, camera, player, frame)
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

        if fighter.stun_timer > 0.0:
            return AnimationClip(anim_name, frame_count=1, frame_time=0.10, loop=True)

        if fighter.is_dodging:
            return AnimationClip(anim_name, frame_count=1, frame_time=0.10, loop=True)

        if fighter.is_wall_clinging:
            return AnimationClip(anim_name, frame_count=1, frame_time=0.10, loop=True)

        if fighter.is_dashing:
            return AnimationClip(anim_name, frame_count=max(1, frame_count), frame_time=0.08, loop=True)

        if fighter.is_attacking:
            return AnimationClip(anim_name, frame_count=max(1, frame_count), frame_time=0.09, loop=True)

        if fighter.move_state == "run":
            if fighter.character.character_id == "brawler" and anim_name == "walk":
                return AnimationClip(anim_name, frame_count=max(1, frame_count), frame_time=0.11, loop=True)
            return AnimationClip(anim_name, frame_count=max(1, frame_count), frame_time=0.09, loop=True)

        if fighter.move_state in ("airborne", "jump_startup"):
            return AnimationClip(anim_name, frame_count=max(1, frame_count), frame_time=0.12, loop=True)

        return AnimationClip(anim_name, frame_count=max(1, frame_count), frame_time=0.14, loop=True)

    def _resolve_animation_name_and_frames(self, fighter) -> tuple[str, int]:
        sprite_set = self.sprite_sets.get(fighter.character.character_id, {})

        if fighter.stun_timer > 0.0:
            frames = sprite_set.get("dead")
            if frames:
                return "dead", len(frames)

        if fighter.is_dodging:
            if fighter.character.character_id == "swordsman":
                frames = sprite_set.get("run")
                if frames:
                    return "run", len(frames)
            else:
                frames = sprite_set.get("jump")
                if frames:
                    return "jump", len(frames)

        if fighter.is_wall_clinging:
            frames = sprite_set.get("jump")
            if frames:
                return "jump", len(frames)

        if fighter.is_attacking:
            attack_anim = self._map_attack_animation_name(fighter)
            if attack_anim is not None:
                frames = sprite_set.get(attack_anim)
                if frames:
                    return attack_anim, len(frames)

        if fighter.hitstun_timer > 0.0:
            frames = sprite_set.get("hurt")
            if frames:
                return "hurt", len(frames)

        if getattr(fighter, "is_dead", False):
            frames = sprite_set.get("dead")
            if frames:
                return "dead", len(frames)

        if fighter.is_dashing:
            if fighter.character.character_id == "brawler":
                frames = sprite_set.get("run")
                if frames:
                    return "run", len(frames)

            frames = sprite_set.get("run")
            if frames:
                return "run", len(frames)

        if fighter.move_state == "run":
            if fighter.character.character_id == "brawler":
                frames = sprite_set.get("walk")
                if frames:
                    return "walk", len(frames)

            frames = sprite_set.get("run")
            if frames:
                return "run", len(frames)

        if fighter.move_state in ("airborne", "jump_startup"):
            frames = sprite_set.get("jump")
            if frames:
                return "jump", len(frames)

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

    def _get_current_frame_surface(self, fighter, player: AnimationPlayer) -> pygame.Surface | None:
        sprite_set = self.sprite_sets.get(fighter.character.character_id)
        if not sprite_set:
            return None

        anim_name, _ = self._resolve_animation_name_and_frames(fighter)
        frames = sprite_set.get(anim_name)
        if not frames:
            return None

        fixed_index = self._get_forced_frame_index(fighter, anim_name, len(frames))
        if fixed_index is not None:
            return frames[fixed_index]

        return frames[player.frame_index % len(frames)]

    def _get_forced_frame_index(self, fighter, anim_name: str, frame_count: int) -> int | None:
        cid = fighter.character.character_id

        if fighter.stun_timer > 0.0 and anim_name == "dead":
            if cid == "brawler":
                return self._safe_frame_index(1, frame_count)
            if cid == "swordsman":
                return self._safe_frame_index(1, frame_count)
            if cid == "gunner":
                return self._safe_frame_index(3, frame_count)

        if fighter.is_wall_clinging and anim_name == "jump":
            if cid == "brawler":
                return self._safe_frame_index(7, frame_count)
            if cid == "gunner":
                return self._safe_frame_index(5, frame_count)
            if cid == "swordsman":
                return self._safe_frame_index(3, frame_count)

        if fighter.is_dodging:
            if cid == "swordsman" and anim_name == "run":
                return self._safe_frame_index(4, frame_count)
            if cid == "brawler" and anim_name == "jump":
                return self._safe_frame_index(2, frame_count)
            if cid == "gunner" and anim_name == "jump":
                return self._safe_frame_index(3, frame_count)

        return None

    def _safe_frame_index(self, wanted: int, frame_count: int) -> int:
        if frame_count <= 0:
            return 0
        if wanted < 0:
            return 0
        if wanted >= frame_count:
            return frame_count - 1
        return wanted

    def _draw_sprite(
        self,
        surface: pygame.Surface,
        fighter,
        camera,
        player: AnimationPlayer,
        frame: pygame.Surface,
    ) -> None:
        if fighter.facing < 0:
            frame = pygame.transform.flip(frame, True, False)

        # 캐릭터 크기 원래 쪽으로 다시 키움
        target_h = int(fighter.height * camera.zoom * 1.55)
        target_w = int(self.FRAME_W * (target_h / self.FRAME_H))

        if target_w <= 0 or target_h <= 0:
            return

        scaled = pygame.transform.scale(frame, (target_w, target_h))

        overlay_color = self._get_state_overlay_color(fighter)
        if overlay_color is not None:
            scaled = self._apply_overlay_only_on_visible_pixels(scaled, overlay_color)

        if fighter.invuln_timer > 0.0 and (player.frame_index % 2 == 0):
            scaled = scaled.copy()
            flash = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 60))
            flash.blit(scaled, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            scaled.blit(flash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        center_sx, center_sy = camera.world_to_screen(fighter.pos.x, fighter.pos.y)
        draw_x = center_sx - target_w // 2
        draw_y = center_sy - int(target_h * 0.68)

        surface.blit(scaled, (draw_x, draw_y))

    def _get_state_overlay_color(self, fighter) -> tuple[int, int, int, int] | None:
        if fighter.is_dashing:
            return (70, 140, 255, 75)

        if fighter.is_dodging:
            return (70, 140, 255, 95)

        if fighter.stun_timer > 0.0:
            return (255, 220, 70, 95)

        return None

    def _apply_overlay_only_on_visible_pixels(
        self,
        sprite: pygame.Surface,
        color: tuple[int, int, int, int],
    ) -> pygame.Surface:
        result = sprite.copy()
        w, h = result.get_size()

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill(color)

        alpha_mask = pygame.Surface((w, h), pygame.SRCALPHA)
        alpha_mask.fill((255, 255, 255, 0))

        src_alpha = pygame.surfarray.pixels_alpha(result)
        dst_alpha = pygame.surfarray.pixels_alpha(alpha_mask)
        dst_alpha[:, :] = src_alpha[:, :]
        del src_alpha
        del dst_alpha

        overlay.blit(alpha_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        result.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return result

    def _load_all_sprite_sets(self) -> None:
        self.sprite_sets["brawler"] = self._load_character_sprite_set(
            folder_name="White_Werewolf",
            file_map={
                "idle": "Idle.png",
                "run": "Run.png",
                "walk": "Walk.png",
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
                "walk": "Walk.png",
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
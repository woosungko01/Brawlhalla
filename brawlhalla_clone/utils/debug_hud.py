# utils/debug_hud.py
#
# F1 키로 토글 가능한 디버그 HUD.

import pygame
from entities.fighter import Fighter

_FONT: pygame.font.Font | None = None
_COLOR = (220, 220, 80)
_BG = (0, 0, 0, 160)
_LINE_H = 18


def _get_font() -> pygame.font.Font:
    global _FONT
    if _FONT is None:
        _FONT = pygame.font.SysFont("monospace", 14)
    return _FONT


def draw_debug_hud(surface: pygame.Surface, fighter: Fighter) -> None:
    """파이터 디버그 정보를 화면 좌측 상단에 출력"""
    font = _get_font()

    lines = [
        f"pos        : ({fighter.pos.x:7.1f}, {fighter.pos.y:7.1f})",
        f"vel        : ({fighter.vel.x:7.1f}, {fighter.vel.y:7.1f})",
        f"state      : {fighter.move_state}",
        f"grounded   : {fighter.is_grounded}",
        f"fast_fall  : {fighter.fast_falling}",
        f"facing     : {'→' if fighter.facing > 0 else '←'}",
        "",
        f"jumps_used : {fighter.air.jumps_used} / {fighter.jump_cfg.MAX_AIR_JUMPS}",
        f"total_rises: {fighter.air.total_air_rises_used}",
        "",
        f"jump_start : {fighter.jump_startup_timer:.3f}",
        f"dash_timer : {fighter.dash_timer:.3f}",
        f"dash_dir   : {fighter.dash_dir}",
        "",
        f"touch_wall : {fighter.touching_wall}",
        f"wall_cling : {fighter.is_wall_clinging}",
        f"wall_dir   : {fighter.wall_dir}",
        f"wall_grace : {fighter.wall_detach_grace_timer:.3f}",
    ]

    pad = 6
    w = 260
    h = len(lines) * _LINE_H + pad * 2

    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    bg.fill(_BG)
    surface.blit(bg, (8, 8))

    for i, line in enumerate(lines):
        surf = font.render(line, True, _COLOR)
        surface.blit(surf, (8 + pad, 8 + pad + i * _LINE_H))
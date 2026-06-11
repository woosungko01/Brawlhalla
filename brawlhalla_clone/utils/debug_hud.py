# utils/debug_hud.py
#
# F1 키로 토글 가능한 디버그 HUD.
# 파라미터 튜닝 시 필수.

import pygame
from core.player import Player

_FONT: pygame.font.Font | None = None
_COLOR = (220, 220, 80)
_BG    = (0, 0, 0, 160)
_LINE_H = 18


def _get_font() -> pygame.font.Font:
    global _FONT
    if _FONT is None:
        _FONT = pygame.font.SysFont("monospace", 14)
    return _FONT


def draw_debug_hud(surface: pygame.Surface, player: Player) -> None:
    """플레이어 디버그 정보를 화면 좌측 상단에 출력"""
    font = _get_font()

    lines = [
        f"pos        : ({player.pos.x:7.1f}, {player.pos.y:7.1f})",
        f"vel        : ({player.vel.x:7.1f}, {player.vel.y:7.1f})",
        f"state      : {player.move_state}",
        f"grounded   : {player.is_grounded}",
        f"fast_fall  : {player.fast_falling}",
        f"facing     : {'→' if player.facing > 0 else '←'}",
        "",
        f"jumps_used : {player.air.jumps_used} / {player.jump_cfg.MAX_AIR_JUMPS}",
        f"total_rises: {player.air.total_air_rises_used}",
        "",
        f"jump_start : {player.jump_startup_timer:.3f}",
        f"land_rec   : {player.landing_recovery_timer:.3f}",
        f"dash_timer : {player.dash_timer:.3f}",
        f"dash_dir   : {player.dash_dir}",
        "",
        f"touch_wall  : {player.touching_wall}",
        f"wall_cling  : {player.is_wall_clinging}",
        f"wall_dir    : {player.wall_dir}",
        f"wall_grace  : {player.wall_detach_grace_timer:.3f}",
    ]

    pad = 6
    w = 260
    h = len(lines) * _LINE_H + pad * 2

    # 반투명 배경
    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    bg.fill(_BG)
    surface.blit(bg, (8, 8))

    for i, line in enumerate(lines):
        surf = font.render(line, True, _COLOR)
        surface.blit(surf, (8 + pad, 8 + pad + i * _LINE_H))

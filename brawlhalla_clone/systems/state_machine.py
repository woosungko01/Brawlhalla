from core.player import Player


def update_move_state(player: Player) -> None:
    if player.is_dashing:
        player.move_state = "dashing"
    elif player.jump_startup_timer > 0:
        player.move_state = "jump_startup"
    elif player.landing_recovery_timer > 0 and player.is_grounded:
        player.move_state = "landing"
    elif not player.is_grounded:
        player.move_state = "airborne"
    elif abs(player.vel.x) > 1.0:
        player.move_state = "run"
    else:
        player.move_state = "idle"
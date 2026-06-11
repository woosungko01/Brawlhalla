# systems/state_machine.py

from entities.fighter import Fighter


def update_move_state(fighter: Fighter) -> None:
    if fighter.is_dashing:
        fighter.move_state = "dashing"
    elif fighter.jump_startup_timer > 0:
        fighter.move_state = "jump_startup"
    elif fighter.is_wall_clinging:
        fighter.move_state = "wall_cling"
    elif fighter.landing_recovery_timer > 0 and fighter.is_grounded:
        fighter.move_state = "landing"
    elif not fighter.is_grounded:
        fighter.move_state = "airborne"
    elif abs(fighter.vel.x) > 1.0:
        fighter.move_state = "run"
    else:
        fighter.move_state = "idle"
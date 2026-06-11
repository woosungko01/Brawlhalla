# systems/gravity.py

from entities.fighter import Fighter


def apply_vertical_forces(fighter: Fighter, dt: float) -> None:
    if fighter.is_dodging:
        return

    if fighter.is_grounded:
        if fighter.vel.y > 0:
            fighter.vel.y = 0.0
        fighter.fast_falling = False
        return

    cfg = fighter.gravity_cfg

    wants_fast_fall = bool(fighter.input.down)
    can_fast_fall = fighter.fast_fall_lock_timer <= 0.0

    if fighter.is_wall_clinging:
        fighter.fast_falling = False
    else:
        fighter.fast_falling = wants_fast_fall and can_fast_fall

    gravity = cfg.GRAVITY
    max_fall_speed = cfg.MAX_FALL_SPEED

    if fighter.fast_falling:
        gravity += cfg.FAST_FALL_ACCEL_BONUS
        max_fall_speed = cfg.FAST_FALL_TERMINAL_SPEED

    fighter.vel.y += gravity * dt

    if fighter.vel.y > max_fall_speed:
        fighter.vel.y = max_fall_speed

    if fighter.is_wall_clinging and fighter.vel.y > cfg.WALL_SLIDE_SPEED:
        fighter.vel.y = cfg.WALL_SLIDE_SPEED
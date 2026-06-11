# systems/movement.py

from entities.fighter import Fighter


def _move_toward(value: float, target: float, max_delta: float) -> float:
    if value < target:
        return min(value + max_delta, target)
    elif value > target:
        return max(value - max_delta, target)
    return value


def apply_horizontal_control(fighter: Fighter, dt: float) -> None:
    if fighter.is_dodging:
        return

    cfg = fighter.move_cfg
    move_x = fighter.input.move_x

    if move_x != 0:
        fighter.facing = move_x

    if fighter.is_grounded:
        accel = cfg.GROUND_ACCEL
        friction = cfg.GROUND_FRICTION
        max_spd = cfg.MAX_RUN_SPEED
    else:
        accel = cfg.AIR_ACCEL
        friction = cfg.AIR_DRAG
        max_spd = cfg.MAX_AIR_SPEED

    if move_x != 0:
        target = move_x * max_spd
        fighter.vel.x = _move_toward(fighter.vel.x, target, accel * dt)
    else:
        fighter.vel.x = _move_toward(fighter.vel.x, 0.0, friction * dt)
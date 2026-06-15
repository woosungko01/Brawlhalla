# systems/fighter_combat.py

import pygame
from combat.pending_effects import PendingLaunch


def tick_combat_timers(fighter, dt: float) -> None:
    if fighter.attack_timer > 0.0:
        fighter.attack_timer = max(0.0, fighter.attack_timer - dt)

    if fighter.ultimate_timer > 0.0:
        fighter.ultimate_timer = max(0.0, fighter.ultimate_timer - dt)

    if fighter.stun_timer > 0.0:
        fighter.stun_timer = max(0.0, fighter.stun_timer - dt)

    if fighter.hitstun_timer > 0.0:
        fighter.hitstun_timer = max(0.0, fighter.hitstun_timer - dt)

    if fighter.attack_tick_timer > 0.0:
        fighter.attack_tick_timer = max(0.0, fighter.attack_tick_timer - dt)


def apply_pending_launch_if_ready(fighter) -> None:
    if fighter.stun_timer > 0.0:
        return

    if fighter.pending_launch is None:
        return

    launch = fighter.pending_launch
    fighter.pending_launch = None

    fighter.vel.x = launch.vx
    fighter.vel.y = launch.vy
    fighter.hitstun_timer = launch.hitstun


def try_start_attack(fighter) -> None:
    if fighter.is_attacking:
        return
    if fighter.stun_timer > 0.0:
        return
    if fighter.hitstun_timer > 0.0:
        return

    attack = fighter.character.resolve_basic_attack(fighter)
    if attack is None:
        return

    fighter.start_attack(attack)


def try_start_ultimate(fighter) -> None:
    if fighter.is_attacking:
        return
    if fighter.stun_timer > 0.0:
        return
    if fighter.hitstun_timer > 0.0:
        return
    if not fighter.ultimate_ready:
        return

    fighter.character.try_start_ultimate(fighter)


def get_current_active_window_index(fighter) -> int | None:
    if fighter.current_attack is None:
        return None

    elapsed = fighter.attack_total_time - fighter.attack_timer

    for i, (start, end) in enumerate(fighter.current_attack.active_windows):
        if start <= elapsed <= end:
            return i

    return None


def is_attack_active(fighter) -> bool:
    return get_current_active_window_index(fighter) is not None


def get_attack_hitbox(fighter):
    if fighter.current_attack is None:
        return None

    if fighter.current_attack.name != "ultimate" and not is_attack_active(fighter):
        return None

    return fighter.character.get_attack_hitbox(fighter)


def update_attack(attacker, targets: list, dt: float) -> None:
    if attacker.stun_timer > 0.0:
        attacker.vel.x = 0.0
        attacker.vel.y = 0.0
        return

    if attacker.hitstun_timer > 0.0:
        return

    if not attacker.is_attacking or attacker.current_attack is None:
        return

    attack = attacker.current_attack

    if attack.locks_horizontal_movement:
        attacker.vel.x = 0.0
    elif attack.dash_velocity_x != 0.0:
        attacker.vel.x = attacker.facing * attack.dash_velocity_x
    else:
        attacker.vel.x = attacker.input.move_x * attacker.move_cfg.MAX_RUN_SPEED

    if attack.repeated_hit_interval is not None:
        if attacker.attack_tick_timer <= 0.0:
            hitbox = get_attack_hitbox(attacker)
            if hitbox is not None:
                for target in targets:
                    if target is attacker:
                        continue
                    try_hit_target(attacker, target, hitbox)
            attacker.attack_tick_timer = attack.repeated_hit_interval
    else:
        window_index = get_current_active_window_index(attacker)

        if window_index is not None:
            # 단일 히트 공격
            if not attack.allow_multi_hit:
                if not attacker.attack_has_hit:
                    hitbox = get_attack_hitbox(attacker)
                    if hitbox is not None:
                        for target in targets:
                            if target is attacker:
                                continue
                            try_hit_target(attacker, target, hitbox)

            # 멀티 히트 공격: active window마다 한 번씩
            else:
                if window_index not in attacker.attack_hit_windows:
                    hitbox = get_attack_hitbox(attacker)
                    if hitbox is not None:
                        hit_any = False
                        for target in targets:
                            if target is attacker:
                                continue
                            if try_hit_target(attacker, target, hitbox):
                                hit_any = True

                        attacker.attack_hit_windows.add(window_index)
                        if hit_any:
                            attacker.attack_has_hit = True

    if attacker.attack_timer <= 0.0:
        attacker.end_attack()


def try_hit_target(attacker, target, hitbox: pygame.Rect) -> bool:
    target_rect = pygame.Rect(
        int(target.rect_x),
        int(target.rect_y),
        target.width,
        target.height,
    )

    if not hitbox.colliderect(target_rect):
        return False

    if target.invuln_timer > 0.0:
        return False

    effect = attacker.character.get_hit_effect(attacker, target)

    target.damage.add_damage(effect.damage)

    if effect.delayed_launch and effect.stun > 0.0:
        target.vel.x = 0.0
        target.vel.y = 0.0
        target.stun_timer = effect.stun
        target.pending_launch = PendingLaunch(
            vx=effect.vx,
            vy=effect.vy,
            hitstun=effect.hitstun,
        )
    else:
        target.vel.x = effect.vx
        target.vel.y = effect.vy
        target.hitstun_timer = effect.hitstun

    attacker.attack_has_hit = True
    return True
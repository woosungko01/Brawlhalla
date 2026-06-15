# systems/fighter_combat.py
# 파이터 전투 처리 파일
# - 공격 시작 / 궁극기 시작
# - 현재 공격 활성화 판정
# - 히트박스 생성 및 타격 처리
# - 무적(invuln), KO/dead 상태 무시 처리 포함

import pygame


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


def try_start_attack(fighter) -> None:
    if fighter.is_attacking:
        return
    if fighter.stun_timer > 0.0:
        return
    if fighter.hitstun_timer > 0.0:
        return
    if getattr(fighter, "is_dead", False):
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
    if getattr(fighter, "is_dead", False):
        return
    if not fighter.ultimate_ready:
        return

    fighter.character.try_start_ultimate(fighter)


def is_attack_active(fighter) -> bool:
    if fighter.current_attack is None:
        return False

    elapsed = fighter.attack_total_time - fighter.attack_timer
    return fighter.current_attack.active_start <= elapsed <= fighter.current_attack.active_end


def get_attack_hitbox(fighter):
    if fighter.current_attack is None:
        return None

    if fighter.current_attack.name != "ultimate" and not is_attack_active(fighter):
        return None

    return fighter.character.get_attack_hitbox(fighter)


def update_attack(attacker, targets: list, dt: float) -> None:
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
        if is_attack_active(attacker) and not attacker.attack_has_hit:
            hitbox = get_attack_hitbox(attacker)
            if hitbox is not None:
                for target in targets:
                    if target is attacker:
                        continue
                    try_hit_target(attacker, target, hitbox)

    if attacker.attack_timer <= 0.0:
        attacker.end_attack()


def try_hit_target(attacker, target, hitbox: pygame.Rect) -> None:
    # 죽은 상태면 무시
    if getattr(target, "is_dead", False):
        return

    # KO 처리 중이면 무시
    if getattr(target, "is_ko", False):
        return

    # 무적 상태면 무시
    if getattr(target, "invuln_timer", 0.0) > 0.0:
        return

    target_rect = pygame.Rect(
        int(target.rect_x),
        int(target.rect_y),
        target.width,
        target.height,
    )

    if not hitbox.colliderect(target_rect):
        return

    effect = attacker.character.get_hit_effect(attacker, target)

    target.damage.add_damage(effect.damage)
    target.vel.x = effect.vx
    target.vel.y = effect.vy
    target.hitstun_timer = effect.hitstun

    attacker.attack_has_hit = True
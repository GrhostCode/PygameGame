import math
import pygame

_last_move_by_key = {}

def get_next_step(current_x, current_y, target_x, target_y, step_size=5, delay_ms=20, key=None, now_ms=None):
    """
    Return next (x, y) toward (target_x, target_y) by step_size pixels.
    Movement is rate-limited independently per 'key'.
    - key: any hashable per-player identifier (e.g., id(player) or an index)
    - delay_ms: min milliseconds between moves for THIS key
    - now_ms: optional time override (milliseconds) for deterministic simulation
    """
    if key is None:
        key = "_shared"

    now = pygame.time.get_ticks() if now_ms is None else now_ms
    last = _last_move_by_key.get(key, 0)
    if now - last < delay_ms:
        return int(current_x), int(current_y)

    _last_move_by_key[key] = now

    dx = target_x - current_x
    dy = target_y - current_y
    dist = math.hypot(dx, dy)
    if dist == 0:
        return int(target_x), int(target_y)

    if step_size >= dist:
        return int(target_x), int(target_y)

    nx = current_x + (dx / dist) * step_size
    ny = current_y + (dy / dist) * step_size
    return int(nx), int(ny)

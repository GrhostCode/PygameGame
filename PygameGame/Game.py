import pygame, random, json, Move, JsonToMatplotlibPT1, JsonToMatplotlibPT2
import math
import os

runs = 100
food_start = 10
food_step = 1
duration_ms = 300

playerAmount = 15
haveDelay = False
reveal_delay = 100

SCREEN_WIDTH  = 1000
SCREEN_HEIGHT = 1000
RECT_W = 50
RECT_H = 50

runSpeed = 400
MAX_AGE  = 100

MOVE_INTERVAL_MS = int(500 / runSpeed)
STEP_DELAY_MS    = int(25  / runSpeed)

DAY_MS = int(4000 / runSpeed)
HALF_DAY_MS = DAY_MS // 2

MATE_FOOD_THRESHOLD = 80
MATE_GAP = 75

base = os.path.dirname(__file__)

# ----------------------------
# Helpers
# ----------------------------
def write_file(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def dist_rect_centers(r1: pygame.Rect, r2: pygame.Rect) -> float:
    return math.hypot(r2.centerx - r1.centerx, r2.centery - r1.centery)

class player:
    def __init__(self, X, Y, W, H):
        self.pygameDraw = pygame.Rect(X, Y, W, H)
        self.tx = X
        self.ty = Y
        self.speed = 4 * runSpeed
        self.food = 50
        self.mating = False
        self.foodDistance = 180
        self.wantsMate = False
        self.age = 0
        now = pygame.time.get_ticks()
        self.next_target_time = now + random.randint(0, MOVE_INTERVAL_MS)
        self.next_move_time   = now + random.randint(0, STEP_DELAY_MS)

class food:
    def __init__(self, X, Y, W, H):
        self.pygameDraw = pygame.Rect(X, Y, W, H)

# ----------------------------
# Pygame init ONCE
# ----------------------------
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 32)

player_texture = pygame.image.load(os.path.join(base, "player.png")).convert_alpha()
player_texture = pygame.transform.scale(player_texture, (RECT_W, RECT_H))

food_texture = pygame.image.load(os.path.join(base, "food.png")).convert_alpha()
food_texture = pygame.transform.scale(food_texture, (RECT_W, RECT_H))

# Files
plr_path  = os.path.join(base, "plrSave.json")
food_path = os.path.join(base, "foodSave.json")

avg_speeds = []
aborted = False

for run_index in range(runs):
    # ----------------------------
    # RESET simulation state (no window reset)
    # ----------------------------
    foodAmount = food_start + run_index * food_step

    plrList = []
    foodList = []

    mates = []
    current_pairs = []
    partner_of = {}
    pair_targets = {}

    revealed = 0
    next_reveal = pygame.time.get_ticks()

    last_reset_time = pygame.time.get_ticks()
    half_day_time = last_reset_time + HALF_DAY_MS
    mating_mode = False

    # Optional: wipe previous json so each run is clean
    write_file(plr_path, "")
    write_file(food_path, "")

    def spawnFood():
        for _ in range(foodAmount - len(foodList)):
            x = random.randint(0, SCREEN_WIDTH  - RECT_W)
            y = random.randint(0, SCREEN_HEIGHT - RECT_H)
            foodList.append(food(x, y, RECT_W, RECT_H))

    def compute_pair_targets_gap(a, b, gap=MATE_GAP):
        ax, ay = a.pygameDraw.centerx, a.pygameDraw.centery
        bx, by = b.pygameDraw.centerx, b.pygameDraw.centery
        dx, dy = bx - ax, by - ay
        dist = math.hypot(dx, dy)
        if dist == 0:
            ux, uy = 1.0, 0.0
        else:
            ux, uy = dx / dist, dy / dist

        half = gap / 2.0
        mx = (ax + bx) / 2.0
        my = (ay + by) / 2.0

        t1x = mx - ux * half
        t1y = my - uy * half
        t2x = mx + ux * half
        t2y = my + uy * half

        a_tx = clamp(int(t1x - RECT_W  / 2), 0, SCREEN_WIDTH  - RECT_W)
        a_ty = clamp(int(t1y - RECT_H / 2), 0, SCREEN_HEIGHT - RECT_H)
        b_tx = clamp(int(t2x - RECT_W  / 2), 0, SCREEN_WIDTH  - RECT_W)
        b_ty = clamp(int(t2y - RECT_H / 2), 0, SCREEN_HEIGHT - RECT_H)
        return (a_tx, a_ty), (b_tx, b_ty)

    def bind_pair_for_day(a, b, gap=MATE_GAP):
        mates.append((a, b))
        current_pairs.append((a, b))
        partner_of[a] = b
        partner_of[b] = a
        (a_tx, a_ty), (b_tx, b_ty) = compute_pair_targets_gap(a, b, gap=gap)
        pair_targets[a] = (a_tx, a_ty)
        pair_targets[b] = (b_tx, b_ty)
        a.tx, a.ty = a_tx, a_ty
        b.tx, b.ty = b_tx, b_ty
        a.mating = True
        b.mating = True

    def unbind_if_missing(player_obj):
        if player_obj in partner_of:
            other = partner_of[player_obj]
            partner_of.pop(player_obj, None)
            partner_of.pop(other, None)
            for t in current_pairs[:]:
                if player_obj in t or other in t:
                    current_pairs.remove(t)
            pair_targets.pop(player_obj, None)
            pair_targets.pop(other, None)

    def make_offspring(a, b):
        meet_x = (a.pygameDraw.x + b.pygameDraw.x) // 2 + random.randint(-5, 5)
        meet_y = (a.pygameDraw.y + b.pygameDraw.y) // 2 + random.randint(-5, 5)
        meet_x = clamp(meet_x, 0, SCREEN_WIDTH  - RECT_W)
        meet_y = clamp(meet_y, 0, SCREEN_HEIGHT - RECT_H)

        child = player(meet_x, meet_y, RECT_W, RECT_H)
        avg_speed = (a.speed + b.speed) / 2.0
        avg_dist  = (a.foodDistance + b.foodDistance) / 2.0
        child.speed        = max(1, avg_speed * random.uniform(0.007, 1.5))
        child.foodDistance = int(max(10, avg_dist * random.uniform(0.9, 2.5)))
        child.food         = 50
        child.tx = random.randint(0, SCREEN_WIDTH  - RECT_W)
        child.ty = random.randint(0, SCREEN_HEIGHT - RECT_H)
        return child

    def greedy_pair_auto():
        wants = [p for p in plrList if p.wantsMate and p not in partner_of]
        n = len(wants)
        if n < 2:
            return
        cand = []
        for i in range(n):
            for j in range(i + 1, n):
                a = wants[i]
                b = wants[j]
                d = dist_rect_centers(a.pygameDraw, b.pygameDraw)
                vision = min(a.foodDistance, b.foodDistance)
                if d <= vision:
                    cand.append((d, a, b))
        cand.sort(key=lambda x: x[0])
        used = set()
        for _, a, b in cand:
            if a in used or b in used or a in partner_of or b in partner_of:
                continue
            bind_pair_for_day(a, b, gap=MATE_GAP)
            used.add(a); used.add(b)

    # Spawn initial population
    for _ in range(playerAmount):
        x = random.randint(0, SCREEN_WIDTH  - RECT_W)
        y = random.randint(0, SCREEN_HEIGHT - RECT_H)
        plrList.append(player(x, y, RECT_W, RECT_H))
    spawnFood()

    sim_start = pygame.time.get_ticks()
    running_run = True

    # ----------------------------
    # Run simulation for duration_ms
    # ----------------------------
    while running_run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                aborted = True
                running_run = False

        if aborted:
            break

        screen.fill((163, 162, 165))
        now = pygame.time.get_ticks()

        if duration_ms is not None and now - sim_start >= duration_ms:
            running_run = False

        # Day cycle
        if now - last_reset_time >= DAY_MS:
            if mates:
                for (a, b) in mates:
                    if (a in plrList) and (b in plrList) and (a.food >= 75) and (b.food >= 75):
                        child = make_offspring(a, b)
                        plrList.append(child)
                        a.food -= 25
                        b.food -= 25

            for plr in plrList:
                if not plr.mating:
                    plr.food -= 30

            spawnFood()
            last_reset_time = now
            mating_mode = False
            mates = []
            current_pairs = []
            partner_of = {}
            pair_targets = {}
            half_day_time = last_reset_time + HALF_DAY_MS

            for plr in plrList:
                plr.wantsMate = (plr.food >= MATE_FOOD_THRESHOLD)
                plr.mating = False

        # Aging / death
        for p in plrList[:]:
            p.age += 1
            if p.age >= MAX_AGE:
                if p in partner_of:
                    unbind_if_missing(p)
                plrList.remove(p)

        # Wants mate
        for plr in plrList:
            if plr.food >= MATE_FOOD_THRESHOLD:
                plr.wantsMate = True

        greedy_pair_auto()

        if (not mating_mode) and now >= half_day_time:
            mating_mode = True
            for plr in plrList:
                if plr not in partner_of:
                    plr.wantsMate = True
            greedy_pair_auto()

        # Movement / targeting
        for plr in plrList:
            if plr in partner_of:
                tx, ty = pair_targets.get(plr, (plr.tx, plr.ty))
                plr.tx, plr.ty = tx, ty
            else:
                if plr.wantsMate or mating_mode:
                    target_rect = None
                    nearest_dist = None
                    for other in plrList:
                        if other is plr or other in partner_of or not other.wantsMate:
                            continue
                        d = dist_rect_centers(plr.pygameDraw, other.pygameDraw)
                        if d <= plr.foodDistance and (nearest_dist is None or d < nearest_dist):
                            nearest_dist = d
                            target_rect = other.pygameDraw
                    if target_rect is not None:
                        plr.tx = target_rect.x
                        plr.ty = target_rect.y
                        plr.next_target_time = now + MOVE_INTERVAL_MS
                    elif now >= plr.next_target_time:
                        plr.tx = random.randint(0, SCREEN_WIDTH - RECT_W)
                        plr.ty = random.randint(0, SCREEN_HEIGHT - RECT_H)
                        plr.next_target_time = now + MOVE_INTERVAL_MS
                else:
                    nearest_food = None
                    nearest_dist = None
                    for f in foodList:
                        d = dist_rect_centers(plr.pygameDraw, f.pygameDraw)
                        if d <= plr.foodDistance and (nearest_dist is None or d < nearest_dist):
                            nearest_dist = d
                            nearest_food = f
                    if nearest_food is not None:
                        plr.tx = nearest_food.pygameDraw.x
                        plr.ty = nearest_food.pygameDraw.y
                        plr.next_target_time = now + MOVE_INTERVAL_MS
                    elif now >= plr.next_target_time:
                        plr.tx = random.randint(0, SCREEN_WIDTH - RECT_W)
                        plr.ty = random.randint(0, SCREEN_HEIGHT - RECT_H)
                        plr.next_target_time = now + MOVE_INTERVAL_MS

            nx, ny = Move.get_next_step(
                plr.pygameDraw.x, plr.pygameDraw.y,
                plr.tx, plr.ty,
                plr.speed,
                STEP_DELAY_MS,
                key=(sim_start, id(plr))
            )
            plr.pygameDraw.x = nx
            plr.pygameDraw.y = ny

        # Eating / starvation
        for plr in plrList[:]:
            if plr.food <= 0:
                if plr in partner_of:
                    unbind_if_missing(plr)
                plrList.remove(plr)
                continue

            for f in foodList[:]:
                if plr.pygameDraw.colliderect(f.pygameDraw):
                    if plr not in partner_of:
                        foodList.remove(f)
                        plr.food += 50

        for p in plrList:
            if p.food > 200:
                p.food = 200

        # Reveal / draw
        if haveDelay:
            if revealed < len(plrList) and now >= next_reveal:
                revealed += 1
                next_reveal = now + int(reveal_delay / runSpeed)
        else:
            revealed = len(plrList)

        for f in foodList:
            screen.blit(food_texture, (f.pygameDraw.x, f.pygameDraw.y))
        for p in plrList[:revealed]:
            screen.blit(player_texture, (p.pygameDraw.x, p.pygameDraw.y))

        if plrList:
            avg_age = sum(p.age for p in plrList) / len(plrList)
            hud = f"Run {run_index+1}/{runs} | Food: {foodAmount} | Players: {len(plrList)} | Avg age: {avg_age:.1f}"
        else:
            hud = f"Run {run_index+1}/{runs} | Food: {foodAmount} | Players: 0 | Avg age: 0.0"

        screen.blit(font.render(hud, True, (0, 0, 0)), (0, 0))
        pygame.display.update()

        # Save JSON (same as you do)
        data = []
        for p in plrList:
            data.append({
                "x": p.pygameDraw.x, "y": p.pygameDraw.y,
                "w": p.pygameDraw.w, "h": p.pygameDraw.h,
                "speed": p.speed, "food": p.food,
                "foodDistance": p.foodDistance
            })
        write_file(plr_path, "\n".join(json.dumps(p) for p in data))

        food_data = []
        for f in foodList:
            food_data.append({
                "x": f.pygameDraw.x, "y": f.pygameDraw.y,
                "w": f.pygameDraw.w, "h": f.pygameDraw.h
            })
        write_file(food_path, "\n".join(json.dumps(f) for f in food_data))

        clock.tick(60)

    if aborted:
        break

    # ----------------------------
    # End of run: extract + average
    # ----------------------------
    speeds = JsonToMatplotlibPT1.extract_json()
    avg = (sum(speeds) / len(speeds)) if speeds else 0

    avg_speeds.append(avg)
    print(f"Run: {run_index+1}/{runs} | Food={foodAmount} | AvgSpeed={avg}")

# Final plot
print(avg_speeds)
if not aborted:
    JsonToMatplotlibPT2.make_plot(avg_speeds, runs)

pygame.quit()

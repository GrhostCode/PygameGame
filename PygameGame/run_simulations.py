import Game
import JsonToMatplotlibPT1
import JsonToMatplotlibPT2

runs = 50
duration_ms = 5_000
food_start = 10
food_step = 5
r = 1
avg_speeds = []
def runsim():
    global avg_speeds, runs, food_start, food_step, r, duration_ms

    food_amount = food_start + r * food_step
    Game.run_simulation(10, food_amount, duration_ms)
    speeds = JsonToMatplotlibPT1.extract_json()
    avg = sum(speeds) / len(speeds) if speeds else 0
    if avg != 0:
        avg_speeds.append(avg)
        r += 1

while r <= runs:
    runsim()

print(avg_speeds)
JsonToMatplotlibPT2.make_plot(avg_speeds)
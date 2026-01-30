import importlib
import Game
import JsonToMatplotlibPT1
import JsonToMatplotlibPT2

runs = 20
duration_ms = 20_000
food_start = 10
food_step = 5

avg_speeds = []

for r in range(runs):
    food_amount = food_start + r * food_step

    Game = importlib.reload(Game)
    Game.run_simulation(10, food_amount, duration_ms)

    speeds = JsonToMatplotlibPT1.extract_json()
    avg = sum(speeds) / len(speeds) if speeds else 0
    avg_speeds.append(avg)
print(avg_speeds)
JsonToMatplotlibPT2.make_plot(avg_speeds)

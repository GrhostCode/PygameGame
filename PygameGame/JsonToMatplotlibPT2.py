import os
import matplotlib.pyplot as plt, numpy as np, JsonToMatplotlibPT1


def make_plot(values, runs=None, output_path=None):
    if values is None:
        values = []

    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "LatestGraph.png")

    y = np.array(values, dtype=float)
    if runs is None or isinstance(runs, int):
        x = np.arange(1, len(y) + 1)
    else:
        x = np.array(runs)

    if len(x) != len(y):
        raise ValueError(f"x and y lengths differ: {len(x)} vs {len(y)}")

    plt.figure()
    if len(y) == 0:
        plt.title("No data to plot")
        plt.xlabel("Run")
        plt.ylabel("Velocidad Promedio")
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.show()
        return output_path

    if len(y) == 1:
        trend = np.array([y[0]])
    else:
        m, b = np.polyfit(x, y, 1)
        trend = m * x + b

    plt.scatter(x, y, color="tab:blue", zorder=2, label="Velocidad Promedio")
    plt.plot(x, trend, color="tab:orange", zorder=3, linewidth=2, label="Trend")
    plt.xlabel("Run")
    plt.ylabel("Velocidad Promedio")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)

    plt.show()
    return output_path


if __name__ == "__main__":
    make_plot([])

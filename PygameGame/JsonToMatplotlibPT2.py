import matplotlib.pyplot as plt, numpy as np, JsonToMatplotlibPT1
def make_plot(list, runs):
    x = np.array(list)
    y = np.array(runs)
    m, b = np.polyfit(x, y, 1)

    trend = m * x + b

    plt.scatter(x, y)
    plt.plot(x, trend)

    plt.show()

if __name__ == "__main__":
    make_plot()
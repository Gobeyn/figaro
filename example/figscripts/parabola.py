import matplotlib.pyplot as plt
import numpy as np

from matplotlib.figure import Figure
from matplotlib.axes import Axes
from pathlib import Path

from .utils import default_axis_config

from figaro import figarotag


def parabola_function(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    return a * x**2 + b * x + c


@figarotag(name="curve", ext="pdf")
def fig_parabola(save_path: Path) -> None:
    # ------------------------------
    # Settings
    # ------------------------------
    a: float = 1.0
    b: float = 0.0
    c: float = -1.0

    # ------------------------------
    # Define Figure & Axes
    # ------------------------------
    fig: Figure = plt.figure()
    ax: Axes = fig.add_subplot()
    default_axis_config(ax=ax)

    # ------------------------------
    # Plot Line
    # ------------------------------
    x: np.ndarray = np.linspace(0.0, 1.0, 100)
    y: np.ndarray = parabola_function(x=x, a=a, b=b, c=c)
    ax.plot(x, y, color="red", linewidth=1)

    # ------------------------------
    # Save figure
    # ------------------------------
    fig.savefig(fname=str(save_path.resolve()), dpi=300, format="pdf")


@figarotag(name="curve2", ext="pdf")
def fig_parabola2(save_path: Path) -> None:
    # ------------------------------
    # Settings
    # ------------------------------
    a: float = 1.0
    b: float = 0.0
    c: float = -1.0

    # ------------------------------
    # Define Figure & Axes
    # ------------------------------
    fig: Figure = plt.figure()
    ax: Axes = fig.add_subplot()
    default_axis_config(ax=ax)

    # ------------------------------
    # Plot Line
    # ------------------------------
    x: np.ndarray = np.linspace(0.0, 1.0, 100)
    y: np.ndarray = parabola_function(x=x, a=a, b=b, c=c)
    ax.plot(x, y, color="blue", linewidth=1)

    # ------------------------------
    # Save figure
    # ------------------------------
    fig.savefig(fname=str(save_path.resolve()), dpi=300, format="pdf")

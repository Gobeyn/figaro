import matplotlib.pyplot as plt
import numpy as np

from matplotlib.figure import Figure
from matplotlib.axes import Axes
from pathlib import Path

from .utils import default_axis_config

from figaro import figarotag


@figarotag(name="line")
def fig_line(save_path: Path) -> None:
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
    y: np.ndarray = 2.0 * x
    ax.plot(x, y, color="blue", linewidth=1)

    # ------------------------------
    # Save figure
    # ------------------------------
    fig.savefig(fname=str(save_path.resolve()), dpi=300, format="pdf")

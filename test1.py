"""
This example demonstrates some of the plotting items available in pyqtgraph.
"""

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

app = pg.mkQApp("InfiniteLine Example")
win = pg.GraphicsLayoutWidget(show=True, title="Plotting items examples")
win.resize(1000, 600)

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# Create a plot with some random data
p1 = win.addPlot(
    title="Plot Items example", y=np.random.normal(size=100, scale=10), pen=0.5
)
p1.setYRange(-40, 40)

inf3 = pg.InfiniteLine(
    movable=True,
    angle=45,
    pen="g",
    label="diagonal",
    labelOpts={"rotateAxis": [1, 0], "fill": (0, 200, 0, 100), "movable": True},
)

p1.addItem(inf3)
# Add a linear region with a label

if __name__ == "__main__":
    pg.exec()


import pyqtgraph as pg
import numpy as np

from src.main_window import MainWindow

MAX_CITIES = 500
INITIAL_CITIES = 10
RANGE = 10.0

# Create app

app = pg.mkQApp("Traveling Salesman")
mw = MainWindow(MAX_CITIES, INITIAL_CITIES, RANGE)

# Execute

if __name__ == '__main__':
    pg.exec()
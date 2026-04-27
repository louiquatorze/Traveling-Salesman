
import pyqtgraph as pg
import time

from src.controller import Controller

MAX_CITIES = 500
INITIAL_CITIES = 10
RANGE = 10.0

# Create app

app = pg.mkQApp("Traveling Salesman")
controller = Controller(MAX_CITIES, INITIAL_CITIES, RANGE)

# Execute

if __name__ == '__main__':
    try:
        pg.exec()
    finally:
        controller.cleanup()
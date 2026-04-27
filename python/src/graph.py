
import pyqtgraph as pg
import numpy as np

class Graph(pg.PlotWidget):
    def __init__(self, RANGE: float, ASPECT: float):
        super().__init__()

        self.RANGE = RANGE

        self.cities_item = pg.ScatterPlotItem(
            brush=pg.mkBrush(255, 0, 0, 250)
        )
        self.path_item = pg.PlotDataItem(
            pen=pg.mkPen(pg.mkColor(255, 0, 0, 220), width=2), symbol=None
        )
        self.min_path_item = pg.PlotDataItem(
            pen=pg.mkPen(pg.mkColor(0, 255, 0, 100), width=2), symbol=None
        )

        self.plotItem.addItem(self.cities_item)
        self.plotItem.addItem(self.path_item)
        self.plotItem.addItem(self.min_path_item)
        
        self.view = self.plotItem.getViewBox()
        self.view.setXRange(min=0, max=RANGE * ASPECT)
        self.view.setYRange(min=0, max=RANGE)
        self.view.setAspectLocked(True)

    def clearPath(self):
        self.path_item.setData([], [])

    def clearMinPath(self):
        self.min_path_item.setData([], [])

    def mapSceneToView(self, scene_pos):
        return self.view.mapSceneToView(scene_pos)
    
    def setCities(self, pos):
        self.cities_item.setData(pos=pos)
    
    def setMinPath(self, path):
        self.min_path_item.setData(path[:, 0], path[:, 1])

    def setPath(self, path):
        self.path_item.setData(path[:, 0], path[:, 1])
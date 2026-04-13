
import numpy as np
import pyqtgraph as pg
import copy

from pyqtgraph.Qt import QtWidgets, QtGui
from pyqtgraph.Qt.QtCore import Qt
from pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent


from PySide6.QtWidgets import QAbstractSpinBox

from src.graph import Graph
from src.solver import Solver

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, MAX_CITIES, INITIAL_CITIES, RANGE):
        super().__init__()

        self.MAX_CITIES = MAX_CITIES
        self.INITIAL_CITIES = INITIAL_CITIES
        self.RANGE = RANGE

        # Init window

        self.setWindowTitle("Traveling Salesman")
        self.resize(800, 600)
        self.show()

        # Init components

        self.cities = []

        self.createSolver()
        self.createGraph()
        self.createControls()

        # Init graph with random values

        self.random()
    
    def createSolver(self):
        self.solver = Solver()

    def createGraph(self):
        self.graph = Graph(self.RANGE, self.height() / self.width())
        self.setCentralWidget(self.graph)

    def createControls(self):
        controls = QtWidgets.QToolBar("Controls")
        controls.setMovable(False)
        controls.setIconSize(pg.QtCore.QSize(24, 24))
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, controls)
        
        # Init elements of toolbar

        solve_action = QtGui.QAction("Solve", self)
        pause_action = QtGui.QAction("Pause", self)
        random_action = QtGui.QAction("Random", self)

        steps_button = QtWidgets.QRadioButton("Steps")

        self.city_count = QtWidgets.QSpinBox()
        self.city_count.setRange(1, self.MAX_CITIES)
        self.city_count.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.city_count.setValue(self.INITIAL_CITIES)

        self.cities_slider = QtWidgets.QSlider(Qt.Orientation.Vertical)
        self.cities_slider.setMinimum(1)
        self.cities_slider.setMaximum(self.MAX_CITIES)
        self.cities_slider.setValue(self.INITIAL_CITIES)

        self.speed_box = QtWidgets.QDoubleSpinBox()
        self.speed_box.setRange(0.5, 100.0)
        self.speed_box.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.speed_box.setValue(100.0)
        self.speed_box.setDecimals(2)

        self.speed_slider = QtWidgets.QSlider(Qt.Orientation.Vertical)
        self.speed_slider.setMinimum(0.5)
        self.speed_slider.setMaximum(100.0)
        self.speed_slider.setValue(100.0)
        
        # Arrange elements on toolbar

        top_space = QtWidgets.QWidget()
        top_space.setFixedHeight(10)

        solve_button = QtWidgets.QToolButton()
        solve_button.setDefaultAction(solve_action)

        pause_button = QtWidgets.QToolButton()
        pause_button.setDefaultAction(pause_action)

        random_button = QtWidgets.QToolButton()
        random_button.setDefaultAction(random_action)

        group_row1 = QtWidgets.QWidget()
        layout_row1 = QtWidgets.QHBoxLayout(group_row1)
        layout_row1.setContentsMargins(5, 1, 5, 1)
        layout_row1.setSpacing(10)
        layout_row1.addWidget(solve_button)
        layout_row1.addWidget(steps_button)

        group_row2 = QtWidgets.QWidget()
        layout_row2 = QtWidgets.QHBoxLayout(group_row2)
        layout_row2.setContentsMargins(5, 1, 5, 1)
        layout_row2.addWidget(pause_button)
        layout_row2.addStretch(1)

        group_row3 = QtWidgets.QWidget()
        layout_row3 = QtWidgets.QHBoxLayout(group_row3)
        layout_row3.setContentsMargins(5, 1, 5, 1)
        layout_row3.addWidget(random_button)
        layout_row3.addStretch(1)

        group_sliders = QtWidgets.QWidget()
        layout_sliders = QtWidgets.QHBoxLayout(group_sliders)
        layout_sliders.setContentsMargins(5, 1, 5, 1)

        group_cities = QtWidgets.QWidget()
        layout_cities = QtWidgets.QVBoxLayout(group_cities)
        layout_cities.setSpacing(5)
        layout_cities.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout_cities.addWidget(QtWidgets.QLabel("Cities"),  alignment=Qt.AlignmentFlag.AlignHCenter)
        layout_cities.addWidget(self.cities_slider,          alignment=Qt.AlignmentFlag.AlignHCenter)
        layout_cities.addWidget(self.city_count,             alignment=Qt.AlignmentFlag.AlignHCenter)

        group_speed = QtWidgets.QWidget()
        layout_speed = QtWidgets.QVBoxLayout(group_speed)
        layout_speed.setSpacing(5)
        layout_speed.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout_speed.addWidget(QtWidgets.QLabel("Speed"),   alignment=Qt.AlignmentFlag.AlignHCenter)
        layout_speed.addWidget(self.speed_slider,          alignment=Qt.AlignmentFlag.AlignHCenter)
        layout_speed.addWidget(self.speed_box,             alignment=Qt.AlignmentFlag.AlignHCenter)

        layout_sliders.addWidget(group_cities)
        layout_sliders.addWidget(group_speed)

        fill_bottom = QtWidgets.QWidget()
        fill_bottom.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, 
            QtWidgets.QSizePolicy.Policy.Expanding
        )

        # Insert into toolbar

        controls.addWidget(top_space)

        controls.addWidget(group_row1)
        controls.addWidget(group_row2)
        controls.addWidget(group_row3)
        controls.addWidget(group_sliders)

        controls.addWidget(fill_bottom)

        controls.setStyleSheet(
            """
            QToolBar {
                background-color: black;
                border: 1px solid #6F6F6F;
                spacing: 2px;
            }

            QToolButton {
                color: #FAFAFA;
                background-color: #0F0F0F;
                border: #0F0F0F;
                border-radius: 4px;

                padding: 5px;
            }

            QLabel {
                color: #FAFAFA;
                background-color: transparent;
            }

            QRadioButton {
                color: #FAFAFA;
                background-color: 0xFAFAFA;
            }

            QSpinBox {
                color: #FAFAFA;
                background-color: #0F0F0F;
            }

            QDoubleSpinBox {
                color: #FAFAFA;
                background-color: #0F0F0F;
            }

            QSlider:vertical {
                min-height: 250px;
            }
            """
        )

        # Hook up

        solve_action.triggered.connect(self.solve)
        pause_action.triggered.connect(self.pause)
        random_action.triggered.connect(self.random)

        self.cities_slider.valueChanged.connect(self.citiesSliderChanged)
        self.city_count.valueChanged.connect(self.cityCountChanged)
        self.graph.scene().sigMouseClicked.connect(self.clicked)

    def pause(self):
        print("paused")
        pass

    def random(self):
        n = self.city_count.value()
        self.cities = list(np.random.uniform(0, self.RANGE, size=(n, 2)))

        self.graph.setCities(np.array(self.cities))
        self.graph.setPath(np.array([]))

    def clicked(self, event: MouseClickEvent):
        n = len(self.cities) + 1

        if n > self.MAX_CITIES:
            return
        
        scene_pos = event.scenePos()
        pos = self.graph.mapSceneToView(scene_pos)

        self.city_count.setValue(n)
        self.cities_slider.setValue(n)

        self.cities.append([pos.x(), pos.y()])
        self.graph.setCities(np.array(self.cities))
    
    def solve(self):
        path = self.solver.solve(self.cities)
        self.graph.setPath(path)

    def citiesSliderChanged(self):
        n = self.cities_slider.value()
        self.city_count.setValue(n)

    def cityCountChanged(self):
        n = self.city_count.value()
        self.cities_slider.setValue(n)
            
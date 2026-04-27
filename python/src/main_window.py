
import numpy as np
import pyqtgraph as pg

from pyqtgraph.Qt import QtWidgets, QtGui
from pyqtgraph.Qt.QtCore import Qt

from PySide6.QtWidgets import QAbstractSpinBox, QStyle
from PySide6.QtGui import QPainter, QColor

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, MAX_CITIES, INITIAL_CITIES, RANGE):
        super().__init__()

        # Init window

        self.setWindowTitle("Traveling Salesman")
        self.resize(800, 600)

        # Init controls
    
        controls = QtWidgets.QToolBar("Controls")
        controls.setMovable(False)
        controls.setIconSize(pg.QtCore.QSize(24, 24))
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, controls)
        
        # Init elements of toolbar

        self.solve_action = QtGui.QAction("Solve", self)
        self.pause_action = QtGui.QAction("Pause", self)
        self.stop_action = QtGui.QAction("Stop", self)
        self.random_action = QtGui.QAction("Random", self)
        self.clear_action = QtGui.QAction("Clear", self)

        self.city_box = QtWidgets.QSpinBox()
        self.city_box.setRange(0, MAX_CITIES)
        self.city_box.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.city_box.setValue(INITIAL_CITIES)

        self.cities_slider = QtWidgets.QSlider(Qt.Orientation.Vertical)
        self.cities_slider.setMinimum(0)
        self.cities_slider.setMaximum(MAX_CITIES)
        self.cities_slider.setValue(INITIAL_CITIES)

        self.speed_box = QtWidgets.QDoubleSpinBox()
        self.speed_box.setRange(0.5, 100.0)
        self.speed_box.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.speed_box.setValue(100.0)
        self.speed_box.setDecimals(2)

        self.speed_slider = QtWidgets.QSlider(Qt.Orientation.Vertical)
        self.speed_slider.setMinimum(0.5)
        self.speed_slider.setMaximum(100.0)
        self.speed_slider.setValue(100.0)

        self.algorithm_box = QtWidgets.QComboBox()
        self.algorithm_box.addItems(["Iterative", "Recursive", "Genetic"])

        self.gpu_button = QtWidgets.QPushButton("GPU")
        self.gpu_button.setCheckable(True)

        self.benchmark_button = QtWidgets.QPushButton("Benchmark")
        self.benchmark_button.setCheckable(True)
        
        # Arrange elements on toolbar

        # Controls

        group_controls = QtWidgets.QWidget()
        layout_controls = QtWidgets.QVBoxLayout(group_controls)
        layout_controls.setSpacing(5)        
        layout_controls.setContentsMargins(5, 1, 5, 1)

        solve_button = QtWidgets.QToolButton()
        solve_button.setDefaultAction(self.solve_action)

        pause_button = QtWidgets.QToolButton()
        pause_button.setDefaultAction(self.pause_action)

        stop_button = QtWidgets.QToolButton()
        stop_button.setDefaultAction(self.stop_action)

        random_button = QtWidgets.QToolButton()
        random_button.setDefaultAction(self.random_action)

        clear_button = QtWidgets.QToolButton()
        clear_button.setDefaultAction(self.clear_action)

        group_row1 = QtWidgets.QWidget()
        layout_row1 = QtWidgets.QHBoxLayout(group_row1)
        layout_row1.setContentsMargins(1, 1, 1, 1) 
        layout_row1.addWidget(solve_button)
        layout_row1.addStretch(1)

        group_row2 = QtWidgets.QWidget()
        layout_row2 = QtWidgets.QHBoxLayout(group_row2)
        layout_row2.setContentsMargins(1, 1, 1, 1)
        layout_row2.addWidget(pause_button)
        layout_row2.addWidget(stop_button)
        layout_row2.addStretch(1)

        group_row3 = QtWidgets.QWidget()
        layout_row3 = QtWidgets.QHBoxLayout(group_row3)
        layout_row3.setContentsMargins(1, 1, 1, 1)
        layout_row3.addWidget(random_button)
        layout_row3.addWidget(clear_button)
        layout_row3.addStretch(1)

        group_sliders = QtWidgets.QWidget()
        layout_sliders = QtWidgets.QHBoxLayout(group_sliders)

        group_cities = QtWidgets.QWidget()
        layout_cities = QtWidgets.QVBoxLayout(group_cities)
        layout_cities.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout_cities.addWidget(QtWidgets.QLabel("Cities"),  alignment=Qt.AlignmentFlag.AlignHCenter)
        layout_cities.addWidget(self.cities_slider,          alignment=Qt.AlignmentFlag.AlignHCenter)
        layout_cities.addWidget(self.city_box,               alignment=Qt.AlignmentFlag.AlignHCenter)

        group_speed = QtWidgets.QWidget()
        layout_speed = QtWidgets.QVBoxLayout(group_speed)
        layout_speed.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout_speed.addWidget(QtWidgets.QLabel("Speed"),   alignment=Qt.AlignmentFlag.AlignHCenter)
        layout_speed.addWidget(self.speed_slider,           alignment=Qt.AlignmentFlag.AlignHCenter)
        layout_speed.addWidget(self.speed_box,              alignment=Qt.AlignmentFlag.AlignHCenter)

        layout_sliders.addWidget(group_cities)
        layout_sliders.addWidget(group_speed)

        layout_controls.addWidget(QtWidgets.QLabel("Controls:"))
        layout_controls.addWidget(group_row1)
        layout_controls.addWidget(group_row2)
        layout_controls.addWidget(group_row3)
        layout_controls.addWidget(group_sliders)

        # Algorithm

        group_algorithm = QtWidgets.QWidget()
        layout_algorithm = QtWidgets.QVBoxLayout(group_algorithm)
        layout_algorithm.setSpacing(5)
        layout_algorithm.setContentsMargins(5, 1, 5, 1)

        layout_algorithm.addWidget(QtWidgets.QLabel("Algorithm:"))
        layout_algorithm.addWidget(self.gpu_button)
        layout_algorithm.addWidget(self.benchmark_button)
        layout_algorithm.addWidget(self.algorithm_box)
        
        # Filler

        top_space = QtWidgets.QWidget()
        top_space.setFixedHeight(10)

        fill_bottom = QtWidgets.QWidget()
        fill_bottom.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, 
            QtWidgets.QSizePolicy.Policy.Expanding
        )

        # Insert into toolbar

        controls.addWidget(top_space)
        controls.addWidget(group_controls)
        controls.addWidget(group_algorithm)
        controls.addWidget(fill_bottom)

        # Style

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
                border: #0F0F0F;
                border-radius: 4px;
            }

            QDoubleSpinBox {
                color: #FAFAFA;
                background-color: #0F0F0F;
                border: #0F0F0F;
                border-radius: 4px;
            }

            QComboBox {
                color: #FAFAFA;
                background-color: #0F0F0F;
                border: #0F0F0F;
                border-radius: 4px;
            }
                    
            QComboBox QAbstractItemView {
                background-color: #0F0F0F;
                color: #FAFAFA;
            }

            QSlider:vertical {
                min-height: 250px;
            }
            """
        )
    
    def setPaused(self, paused):
        self.pause_action.setText("Play" if paused else "Pause")

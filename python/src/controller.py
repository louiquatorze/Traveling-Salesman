
import numpy as np
import time

from src.main_window import MainWindow

from pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent
from PySide6.QtCore import QThread, QObject, Signal, Slot

from src.solver_worker import SolverWorker
from src.graph import Graph
from src.memory import Memory
from src.init_data import InitData
from src.method import Method
from src.benchmark import Benchmark

class Controller(QObject):
    ready = Signal()
    stop_worker = Signal()

    set_paused = Signal(bool)
    set_delay = Signal(float)

    #   (<method>, <gpu?>, <benchmark?>)
    supported = {
        (Method.ITERATIVE, False, True),
        (Method.ITERATIVE, False, False)
    }

    def __init__(self, MAX_CITIES, INITIAL_CITIES, RANGE):
        super().__init__()

        self.MAX_CITIES = MAX_CITIES
        self.INITIAL_CITIES = INITIAL_CITIES
        self.RANGE = RANGE

        self.cities = []

        self.memory = None
        self.solver_thread = None
        self.solver_worker = None

        self.worker_running = False
        self.worker_paused = False

        self.createMainWindow()
        self.createGraph()
        self.createMemory()

        self.connectControls()
        self.random()
    
    def createMainWindow(self):
        self.main_window = MainWindow(self.MAX_CITIES, self.INITIAL_CITIES, self.RANGE)
        self.main_window.show()

    def createGraph(self):
        self.graph = Graph(self.RANGE, self.main_window.height() / self.main_window.width())
        self.main_window.setCentralWidget(self.graph)

    def createMemory(self):
        self.memory = Memory()

    def connectControls(self):
        self.main_window.solve_action.triggered.connect(self.solve)
        self.main_window.pause_action.triggered.connect(self.pause)
        self.main_window.stop_action.triggered.connect(self.stop)
        self.main_window.random_action.triggered.connect(self.random)
        self.main_window.clear_action.triggered.connect(self.clear)

        self.main_window.cities_slider.valueChanged.connect(self.citiesSliderChanged)
        self.main_window.city_box.valueChanged.connect(self.cityBoxChanged)

        self.main_window.speed_slider.valueChanged.connect(self.speedSliderChanged)
        self.main_window.speed_box.valueChanged.connect(self.speedBoxChanged)

        self.graph.scene().sigMouseClicked.connect(self.clicked)

    def pause(self):
        self.worker_paused = not self.worker_paused
        self.set_paused.emit(self.worker_paused)
        self.main_window.setPaused(self.worker_paused)

    def random(self):
        if self.worker_running:
            return
        
        self.graph.clearPath()
        self.graph.clearMinPath()

        n = self.main_window.city_box.value()

        if n == 0:
            self.cities = []
            self.graph.clearCities()
        else:
            self.cities = list(np.random.uniform(0, self.RANGE, size=(n, 2)))
            self.graph.setCities(np.array(self.cities))

    def clear(self):
        if self.worker_running:
            return
        
        self.graph.clearPath()
        self.graph.clearMinPath()
        self.graph.clearCities()

        self.cities = []

    def clicked(self, event: MouseClickEvent):
        if self.worker_running:
            return
        
        n = len(self.cities) + 1
        
        if n > self.MAX_CITIES:
            return
        
        scene_pos = event.scenePos()
        pos = self.graph.mapSceneToView(scene_pos)

        self.main_window.city_box.setValue(n)
        self.main_window.cities_slider.setValue(n)

        self.cities.append([pos.x(), pos.y()])
        self.graph.setCities(np.array(self.cities))

    def solve(self):
        self.destroySolverThread()

        if len(self.cities) <= 1:
            print("[Controller] Must have at least two cities to solve.")
            return
        
        self.init_data = InitData(
            np.array(self.cities, dtype=np.float64),
            self.main_window.algorithm_box.currentIndex(),
            self.main_window.gpu_button.isChecked(),
            self.main_window.benchmark_button.isChecked()
        )

        supported = (self.init_data.method, self.init_data.gpu, self.init_data.benchmark) in self.supported
        if not supported:
            print("[Controller] The algorithm specifications are not supported.")
            return
        
        self.graph.clearPath()
        self.graph.clearMinPath()

        self.createSolverThread(self.init_data, indent=0)

        if self.init_data.benchmark:
            self.solveBenchmark()
        else:
            self.solveBatches()

        print("[Controller] Starting solver thread")

        self.solver_thread.start()
        self.worker_running = True

    def solveBenchmark(self):
        self.solver_worker.benchmark.connect(self.receiveBenchmark)

    @Slot(Benchmark)
    def receiveBenchmark(self, benchmark: Benchmark):
        min_path = np.zeros((len(self.init_data.cities) + 1, 2))
        min_path[0] = self.cities[0]
        min_path[-1] = self.cities[0]
        min_path[1:-1] = self.init_data.cities[benchmark.indices]
        
        self.graph.setMinPath(min_path)
    
    def solveBatches(self):
        self.solver_worker.new_paths.connect(self.renderPaths)
        self.solver_worker.solved.connect(self.onSolved)

        self.set_paused.connect(self.solver_worker.setPaused)
        self.set_delay.connect(self.solver_worker.setDelay)

        self.stop_worker.connect(self.solver_worker.stop)

        self.ready.connect(self.solver_worker.getPaths)
        self.ready.emit()

    def stop(self):
        print("[Controller] Stopping solver")
        self.destroySolverThread()
    
    def citiesSliderChanged(self):
        n = self.main_window.cities_slider.value()
        
        self.main_window.city_box.blockSignals(True)
        self.main_window.city_box.setValue(n)
        self.main_window.city_box.blockSignals(False)

    def cityBoxChanged(self):
        n = self.main_window.city_box.value()
        
        self.main_window.cities_slider.blockSignals(True)
        self.main_window.cities_slider.setValue(n)
        self.main_window.cities_slider.blockSignals(False)
    
    def speedSliderChanged(self):
        n = self.main_window.speed_slider.value()

        self.main_window.speed_box.blockSignals(True)
        self.main_window.speed_box.setValue(n)
        self.main_window.speed_box.blockSignals(False)

        self.set_delay.emit(self.calcDelay())

    def speedBoxChanged(self):
        n = self.main_window.speed_box.value()

        self.main_window.speed_box.blockSignals(True)
        self.main_window.speed_slider.setValue(n)
        self.main_window.speed_box.blockSignals(False)

        self.set_delay.emit(self.calcDelay())

    def calcDelay(self):
        perc = self.main_window.speed_box.value()
        return (1.0 - perc * 0.01) * 0.8

    @Slot(np.ndarray, int)
    def renderPaths(self, paths, min_path):
        paths_copy = paths.copy()

        if min_path < 0:
            self.graph.setPath(paths_copy[0])
        else:
            self.graph.setMinPath(paths_copy[min_path])

        self.ready.emit()

    @Slot()
    def onSolved(self):
        print("[Controller] Solved.")
        self.graph.clearPath()
    
    def createSolverThread(self, init_data, indent = 0):
        print(f"{ " " * indent }[Controller] Creating new solver thread")

        self.solver_thread = QThread()
        self.solver_worker = SolverWorker(self.memory, init_data)
        self.solver_worker.moveToThread(self.solver_thread)
        self.solver_thread.started.connect(self.solver_worker.init)
        self.solver_thread.finished.connect(self.onThreadFinished)

    def onThreadFinished(self):
        if self.solver_worker is not None:
            self.solver_worker.deleteLater()
            self.solver_worker = None

        if self.solver_thread is not None:
            self.solver_thread.deleteLater()
            self.solver_thread = None
            
        self.worker_running = False

    def destroySolverThread(self, indent = 0):
        if self.solver_thread is None:
            return
        
        try:
            if not self.solver_thread.isRunning():
                self.worker_running = False
                return
        except RuntimeError:
            print(f"{ " " * indent }[Controller] Ghost thread")
            self.worker_running = False

            self.solver_thread = None
            self.solver_worker = None
            return
        
        print(f"{ " " * indent }[Controller] Thread still active, cleaning up.")

        self.stop_worker.emit()

        self.solver_thread.blockSignals(True)
        if self.solver_worker:
            self.solver_worker.blockSignals(True)
        
        if not self.solver_thread.wait(5000):
            print("[Controller] Thread timed out! Forcing termination...")
            self.solver_thread.terminate()
            self.solver_thread.wait()
        
        self.solver_thread = None
        self.solver_worker = None

        self.worker_running = False   

        print(f"{ " " * indent }[Controller] Threds dead babe. Threds dead.")

    def cleanup(self, indent = 0):
        print(f"{ " " * indent }[Controller] Cleaning up controller")

        self.destroySolverThread(indent + 1)

        if self.memory is not None:
            self.memory.cleanup(indent + 1)
            self.memory = None
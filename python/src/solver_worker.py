
import time
import numpy as np

from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot, QProcess, Qt

from src.memory import Memory
from src.init_data import InitData
from src.benchmark import Benchmark

class SolverWorker(QObject):
    waiting = Signal()

    new_paths = Signal(np.ndarray, int)
    solved = Signal()

    benchmark = Signal(Benchmark)
    
    def __init__(self, memory: Memory, init_data: InitData):
        super().__init__()

        self.solver_process = None

        self.init_data = init_data
        self.memory = memory

        self._running = True
        
    def init(self, paused: bool = False, delay: float = 0.0):
        print("[Worker] Initializing")
        
        self.waiting.connect(self.getPaths, type=Qt.ConnectionType.QueuedConnection)

        self.changed_path_size = len(self.init_data.cities) - 1

        self.memory.resetSems()
        self.startProcess()
        self.memory.sendInitData(self.init_data)

        if self.init_data.benchmark:
            self.solver_process.finished.connect(self.getBenchmark)
        else:
            self.paused = paused
            self.delay = delay

            self.last_time = time.time() - self.delay

            self.path_buffer = np.zeros((1, len(self.init_data.cities) + 1, 2), dtype=np.float64)
            self.path_buffer[:, 0] = self.init_data.cities[0]
            self.path_buffer[:, -1] = self.init_data.cities[0]
    
    def startProcess(self):
        PROCESS_EXE = Path(__file__).resolve().parent.parent.parent / "build/travelingSalesman"
        
        self.solver_process = QProcess(self)
        self.solver_process.setProgram(str(PROCESS_EXE))
        self.solver_process.setArguments(self.memory.getIPCArgs())
        
        self.solver_process.readyReadStandardOutput.connect(self.printOut)
        self.solver_process.readyReadStandardError.connect(self.printErr)
        self.solver_process.finished.connect(self.onProcessFinished)

        self.solver_process.start()

    @Slot(bool)
    def setPaused(self, paused):
        self.paused = paused

    @Slot(float)
    def setDelay(self, delay):
        self.delay = delay

    @Slot()
    def printOut(self, indent = 0):
        if not self.solver_process:
            return
        
        data = self.solver_process.readAllStandardOutput().data().decode().strip()
        lines = data.split('\n')

        for line in lines:
            print(f"{ ' ' * indent }[C++ Output] { line }")
    
    @Slot()
    def printErr(self, indent = 0):
        if not self.solver_process:
            return
        
        data = self.solver_process.readAllStandardError().data().decode().strip()
        lines = data.split('\n')

        for line in lines:
            print(f"{ ' ' * indent }[C++ Error] { line }")

    @Slot(int, QProcess.ExitStatus)
    def onProcessFinished(self, exitCode, exitStatus, indent = 0):
        print(f"{ ' ' * indent }[Worker] Subprocess finished")
        if exitStatus == QProcess.ExitStatus.CrashExit:
            print(f"{ ' ' * (indent + 1) }[Worker] Process crashed!")
            self.stop(indent + 2)
        elif exitCode == 0:
            print(f"{ ' ' * (indent + 1) }[Worker] Process exited successfully")
        else:
            print(f"{ ' ' * (indent + 1) }[Worker] Process exited without success")
            self.stop(indent + 2)

    @Slot()
    def getBenchmark(self):
        if not self.memory.isDataAvailable():
            print("[Worker] Failed to get benchmark")
        else:
            print("[Worker] Reading benchmark")
            self.benchmark.emit(self.memory.getBenchmark(self.changed_path_size))

        self.stop()

    @Slot()
    def getPaths(self): 
        if not self._running:
            return
        
        if self.paused:
            time.sleep(0.1)
            self.waiting.emit()
            return
        
        if not self.memory.isDataAvailable(timeout=1000):
            self.waiting.emit()
            return
        
        elapsed_time = time.time() - self.last_time
        remaining_time = self.delay - elapsed_time
        
        if remaining_time > 0.0:
            time.sleep(remaining_time)
            
        pathc = self.memory.getPathCount()
        
        if pathc == 0:
            self.solved.emit()
            self.stop()
            return
        
        min_path = self.memory.getMinPathIndex()
        paths = self.memory.getPathIndices(pathc, self.changed_path_size)
        
        self.path_buffer[:pathc, 1:-1] = self.init_data.cities[paths]

        self.memory.setDataConsumed()
        self.new_paths.emit(self.path_buffer, min_path)
        
        self.last_time = time.time()

    @Slot()
    def stop(self, indent = 0):
        if not self._running:
            return

        self._running = False
        
        print(f"{ ' ' * indent }[Worker] Stopping worker")

        try:
            self.waiting.disconnect(self.getPaths)
        except (TypeError, RuntimeError):
            pass

        self.terminateProcess(indent + 1)
        self.thread().quit()
    
    def terminateProcess(self, indent = 0):
        if self.solver_process is None:
            return
        
        print(f"{ ' ' * indent }[Worker] Cleaning up subprocess")
        
        try:
            self.solver_process.readyReadStandardOutput.disconnect(self.printOut)
            self.solver_process.readyReadStandardError.disconnect(self.printErr)
        except (TypeError, RuntimeError):
            pass

        if self.solver_process.state() != QProcess.ProcessState.NotRunning:
            print(f"{ " " * indent }[Worker] Subprocess still running, terminating")
            self.solver_process.terminate()
            self.memory.setDataConsumed()

            if not self.solver_process.waitForFinished(2000):
                print(f"{ " " * indent }[Worker] Failed to terminate, killing subprocess")
                self.solver_process.kill()
                self.solver_process.waitForFinished()

        print(f"{ ' ' * indent }[Worker] Done. Exit code = { self.solver_process.exitCode() }.")

        self.solver_process.deleteLater()
        self.solver_process = None
    
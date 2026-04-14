
import subprocess
import atexit
import numpy as np

from enum import Enum
from pathlib import Path

class Solver:
    def __init__(self):
        PROJECT_DIR = Path(__file__).resolve().parent.parent.parent

        self.solver_process = subprocess.Popen(
            [PROJECT_DIR / "build/travelingSalesman"], 
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        print(f"Started C++ process with pid: { self.solver_process.pid }")

        atexit.register(self.cleanup)
    
    def cleanup(self):
        if self.solver_process is not None:
            print("Cleaning up subprocess")

            if (poll := self.solver_process.poll()) is None:
                self.solver_process.terminate()
                
                try:
                    self.solver_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.solver_process.kill()
            
            print(f"Done. Exit code = { poll }.")

        self.solver_process = None

    def solve(self, cities, steps):
        line_generator = (f"{ p[0] } { p[1] }\n" for p in cities)

        self.solver_process.stdin.writelines(line_generator)
        self.solver_process.stdin.write("~\n")
        self.solver_process.stdin.flush()

        path_count = len(cities) + 1
        path = []

        print("Receiving from solver process")

        for i in range(path_count):
            line = self.solver_process.stdout.readline()
            parts = line.partition(" ")

            path.append([float(parts[0]), float(parts[2])])
        
        return np.array(path)
        
    def __del__(self):
        self.cleanup()

    
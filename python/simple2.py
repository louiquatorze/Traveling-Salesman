
import time
import atexit
import numpy as np

from pathlib import Path
from src.method import Method
from src.memory import Memory
from src.solver_worker import SolverWorker
from src.init_data import InitData

from multiprocessing.shared_memory import SharedMemory

# Step 0: Init data sent from python -> c++
#
# - cities, algorithm settings
# - python updates init_sem -> c++ reads data
#
# Step 1: Data calculated on c++ side and sent to python
#
# Step 1.1: c++ calculates next batch of paths and writes into shmem
# Step 1.2: python reads next batch of paths from shmem
# Step 1.3: python renders batch, meanwhile Step 1.1 takes place again
#
# Step 2: Process ends (optimal path found / interrupt)
#
# init data : | (int) number of cities | (int) method | (bool) gpu | (bool) benchmark | ([[float, float]]) cities
# batch data: | (int) batch size | path 0 | path 1 | ... | path n |
# path:       | (short) city 0 index | city 1 index | ... | city n index |
#

# Consts

CITIES = np.array([
    [0, 1], [1, 1],
    [0, 0], [1, 0],
    [2, 0], [0, 2],
], dtype=np.float64)

METHOD = Method.ITERATIVE
GPU = False
BENCHMARK = False

# Clean

memory = None
worker = None

def clean():
    if memory is not None:
        memory.cleanup()

    if worker is not None:
        worker.terminateProcess()

atexit.register(clean)

init_data = InitData (
    cities=CITIES,
    method=METHOD,
    gpu=GPU,
    benchmark=BENCHMARK
)

memory = Memory()
memory.sendInitData(init_data)

worker = SolverWorker(memory, init_data)

finished = False
while not finished:
    waiting = True
    while waiting:
        if worker.solver_process.poll() is not None:
            finished = True
            break

        worker.printOut()
        worker.printErr()

        waiting = not memory.isDataAvailable(1)

    pathc = memory.getPathCount()
    
    if pathc == 0:
        finished = True
    
    min_index = memory.getMinPathIndex()
    path = memory.getPathIndices(pathc, len(CITIES) - 1)

    print(pathc, min_index)
    print(path)

    time.sleep(0.1)
    memory.setDataConsumed()
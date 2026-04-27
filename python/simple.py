
import subprocess
import posix_ipc
import struct
import atexit
import time
import os
import numpy as np

from pathlib import Path
from src.method import Method

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

SHM_NAME = "/tsp_shm_buffer"
SEM_INIT_NAME = "/tsp_sem_init"
SEM_AVAILABLE_NAME = "/tsp_sem_available"
SEM_CONSUMED_NAME = "/tsp_sem_consumed"

CITIES = np.array([
    [0, 1], [1, 1],
    [0, 0], [1, 0],
    [2, 0], [0, 2],
], dtype=np.float64)

PROCESS_EXE_PATH = Path(__file__).resolve().parent.parent / "build/travelingSalesman"

SHM_BYTES = 65536
PATH_SIZE = len(CITIES) + 1
CHANGED_PATH_SIZE = len(CITIES) - 1
MAX_BATCH_PATHS = (SHM_BYTES - 4) // (CHANGED_PATH_SIZE * 2)

METHOD = Method.ITERATIVE
GPU = False
BENCHMARK = False

# Clean

try:
    posix_ipc.unlink_semaphore(SEM_INIT_NAME)
except posix_ipc.ExistentialError:
    pass

try:
    posix_ipc.unlink_semaphore(SEM_CONSUMED_NAME)
except posix_ipc.ExistentialError:
    pass

try:
    posix_ipc.unlink_semaphore(SEM_AVAILABLE_NAME)
except posix_ipc.ExistentialError:
    pass

def clean():
    global shm, data_consumed_sem, data_available_sem
    
    if shm is not None:
        try:
            shm.close()
            shm.unlink()
        except (FileNotFoundError, AttributeError):
            pass
    
    def destroy_sem(sem, name):
        if sem is not None:
            try:
                sem.close()
                posix_ipc.unlink_semaphore(name)
            except posix_ipc.ExistentialError:
                pass
    
    destroy_sem(init_sem, SEM_INIT_NAME)
    destroy_sem(data_consumed_sem, SEM_CONSUMED_NAME)
    destroy_sem(data_available_sem, SEM_AVAILABLE_NAME)

atexit.register(clean)

# Init

shm = SharedMemory(name=SHM_NAME, create=True, size=SHM_BYTES)

init_sem = posix_ipc.Semaphore(SEM_INIT_NAME, posix_ipc.O_CREAT | posix_ipc.O_EXCL, initial_value=0)
data_available_sem = posix_ipc.Semaphore(SEM_AVAILABLE_NAME, posix_ipc.O_CREAT | posix_ipc.O_EXCL, initial_value=0)
data_consumed_sem = posix_ipc.Semaphore(SEM_CONSUMED_NAME, posix_ipc.O_CREAT | posix_ipc.O_EXCL, initial_value=1)

solver_process = subprocess.Popen(
    [ PROCESS_EXE_PATH, shm.name, str(SHM_BYTES), init_sem.name, data_available_sem.name, data_consumed_sem.name ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    bufsize=0
)

os.set_blocking(solver_process.stdout.fileno(), False)
os.set_blocking(solver_process.stderr.fileno(), False)

# Create and send init data

init_data_fmt = "=ii??6x"
init_data = struct.pack(
    init_data_fmt, 
    len(CITIES),
    METHOD, 
    GPU, 
    BENCHMARK
)
init_data_size = struct.calcsize(init_data_fmt)

shm.buf[:init_data_size] = init_data
shm.buf[init_data_size:init_data_size + CITIES.nbytes] = CITIES.tobytes()

init_sem.release()

batch_paths_buffer = np.zeros((MAX_BATCH_PATHS, PATH_SIZE, 2), dtype=np.float64)
batch_paths_buffer[:, 0] = CITIES[0]
batch_paths_buffer[:, -1] = CITIES[0]

min_path = []

finished = False
while not finished:
    output = solver_process.stdout.read()
    if output:
        print(f"[C++ Solver]: {output.decode().strip()}")

    err = solver_process.stderr.read()
    if err:
        print(f"[C++ Error]: {err.decode().strip()}")
    
    try:
        data_available_sem.acquire(timeout=2)

        pathc_array = np.ndarray((1,), dtype=np.int32, buffer=shm.buf, offset=0)
        pathc = pathc_array[0]

        min_index_array = np.ndarray((1,), dtype=np.int32, buffer=shm.buf, offset=4)
        min_index = min_index_array[0]
        
        if pathc == 0:
            finished = True
        else:
            path_indices = np.ndarray((pathc, CHANGED_PATH_SIZE), dtype=np.uint16, buffer=shm.buf, offset=8)
            #batch_paths_buffer[:pathc, 1:-1] = CITIES[min_path]
            
            if min_index != -1:
                min_path = path_indices.copy()
        
        data_consumed_sem.release()
    except posix_ipc.BusyError:
        if solver_process.poll() is not None:
            finished = True

min_path_coords = np.zeros((PATH_SIZE, 2), dtype=np.float64)
min_path_coords[0] = CITIES[0]
min_path_coords[-1] = CITIES[0]
min_path_coords[1:-1] = CITIES[min_path]

print(min_path_coords)
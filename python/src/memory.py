
import posix_ipc
import struct
import os
import numpy as np
import glob

from multiprocessing.shared_memory import SharedMemory
from src.init_data import InitData

class Memory:
    def __init__(self):
        self.BYTE_COUNT = 65536

        self.SHM_NAME = "/tsp_shm_buffer"
        self.SEM_INIT_NAME = "/tsp_sem_init"
        self.SEM_DATA_AVAILABLE_NAME = "/tsp_sem_available"
        self.SEM_DATA_CONSUMED_NAME = "/tsp_sem_consumed"

        self.shm = None
        self.sem_init = None
        self.sem_data_available = None
        self.sem_data_consumed = None
        
        self.shm = SharedMemory(self.SHM_NAME, True, self.BYTE_COUNT)

        self.sem_init = posix_ipc.Semaphore(self.SEM_INIT_NAME, posix_ipc.O_CREAT | posix_ipc.O_EXCL, initial_value=0)
        self.sem_data_available = posix_ipc.Semaphore(self.SEM_DATA_AVAILABLE_NAME, posix_ipc.O_CREAT | posix_ipc.O_EXCL, initial_value=0)
        self.sem_data_consumed = posix_ipc.Semaphore(self.SEM_DATA_CONSUMED_NAME, posix_ipc.O_CREAT | posix_ipc.O_EXCL, initial_value=1)

    def getIPCArgs(self):
        return [ 
            self.SHM_NAME,
            str(self.BYTE_COUNT),
            self.SEM_INIT_NAME,
            self.SEM_DATA_AVAILABLE_NAME,
            self.SEM_DATA_CONSUMED_NAME,
        ]

    def resetSems(self):
        def setZero(sem):
            try:
                while True:
                    sem.acquire(timeout=0)
            except posix_ipc.BusyError:
                pass

        def setOne(sem):
            setZero(sem)
            sem.release()
            
        setZero(self.sem_init)  
        setZero(self.sem_data_available)  
        setOne(self.sem_data_consumed)  

    def sendInitData(self, init_data: InitData):
        init_data_fmt = "=ii??6x"
        init_data_struct = struct.pack(
            init_data_fmt, 
            len(init_data.cities),
            init_data.method, 
            init_data.gpu, 
            init_data.benchmark
        )
        init_data_size = struct.calcsize(init_data_fmt)

        self.shm.buf[:init_data_size] = init_data_struct
        self.shm.buf[init_data_size:init_data_size + init_data.cities.nbytes] = init_data.cities.tobytes()

        self.sem_init.release()

    def isDataAvailable(self, timeout = 0):
        try:
            self.sem_data_available.acquire(timeout=timeout)
        except posix_ipc.BusyError:
            return False
        
        return True
    
    def setDataConsumed(self):
        self.sem_data_consumed.release()
    
    def getPathCount(self):
        pathc_array = np.ndarray((1,), dtype=np.int32, buffer=self.shm.buf, offset=0)
        return pathc_array[0]
    
    def getMinPathIndex(self):
        min_index_array = np.ndarray((1,), dtype=np.int32, buffer=self.shm.buf, offset=4)
        return min_index_array[0]

    def getPathIndices(self, pathc, changed_path_size):
        return np.ndarray((pathc, changed_path_size), dtype=np.uint16, buffer=self.shm.buf, offset=8)
    
    def cleanup(self, indent = 0):
        print(f"{ " " * indent }[Memory] Cleaning up memory")
        
        if self.shm is not None:
            try:
                self.shm.close()
                self.shm.unlink()
            except (FileNotFoundError, AttributeError):
                pass
            
            self.shm = None

        def destroy_sem(sem, name):
            if sem is not None:
                try:
                    sem.close()
                    posix_ipc.unlink_semaphore(name)
                except posix_ipc.ExistentialError:
                    pass
        
        destroy_sem(self.sem_init, self.SEM_INIT_NAME)
        destroy_sem(self.sem_data_consumed, self.SEM_DATA_CONSUMED_NAME)
        destroy_sem(self.sem_data_available, self.SEM_DATA_AVAILABLE_NAME)

        self.sem_init = None
        self.sem_data_consumed = None
        self.sem_data_available = None
        
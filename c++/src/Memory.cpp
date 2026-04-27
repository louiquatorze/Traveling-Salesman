
#include "Memory.h"

#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>

#include <cstdlib>
#include <iostream>
#include <thread>
#include <chrono>
#include <string>
#include <memory.h>

Memory::Memory(char* ipcInfo[]) {
    shmBytes = std::stoi(ipcInfo[1]);

    openShm(ipcInfo[0]);
    openSem(semInit, ipcInfo[2]);
    openSem(semDataAvailable, ipcInfo[3]);
    openSem(semDataConsumed, ipcInfo[4]);
}

Memory::~Memory() {
    if (region != MAP_FAILED && region != nullptr) {
        int code = munmap(region, shmBytes);
        region = nullptr;

        if (code == -1) {
            std::cerr << "Failed to unmap shared memory mapping" << std::endl;
            exit(EXIT_FAILURE);
        }
    }

    if (semInit != SEM_FAILED && semInit != nullptr) {
        sem_close(semInit);
        semInit = nullptr;
    }

    if (semDataAvailable != SEM_FAILED && semDataAvailable != nullptr) {
        sem_close(semDataAvailable);
        semDataAvailable = nullptr;
    }

    if (semDataConsumed != SEM_FAILED && semDataConsumed != nullptr) {
        sem_close(semDataConsumed);
        semDataConsumed = nullptr;
    }
}

void Memory::openShm(char* shmName) {
    int fd = shm_open(shmName, O_RDWR, S_IRWXU);

    if (fd == -1) {
        std::cerr << "Failed to access shared memory" << std::endl;
        exit(EXIT_FAILURE);
    }

    region = mmap(
        NULL, 
        shmBytes, 
        PROT_READ | PROT_WRITE, 
        MAP_SHARED,
        fd,
        0
    );

    close(fd);

    if (region == MAP_FAILED) {
        std::cerr << "Failed to mmap" << std::endl;
        exit(EXIT_FAILURE);
    }

    batchData = nullptr;
    initData = reinterpret_cast<InitData*>(region);
}

void Memory::openSem(sem_t*& sem, char* semName) {
    sem = sem_open(semName, 0, O_RDWR);

    if (sem == SEM_FAILED) {
        std::cerr << "Failed to open semaphore" << std::endl;
        exit(EXIT_FAILURE);
    }
}

void Memory::awaitInitData() {
    sem_wait(semInit);
    maxPaths = (shmBytes - sizeof(BatchData::Header)) / ((initData->cityCount - 1) * 2);
}

void Memory::disposeInitData() {
    batchData = static_cast<BatchData*>(region);
    benchmarkData = static_cast<BenchmarkData*>(region);
    initData = nullptr;
}

void Memory::setBenchmarkDataTime(u32 time_ms) {
    this->benchmarkData->time_ms = time_ms;
}

void Memory::setBenchmarkDataIndices(std::vector<u16>& indices) {
    for (i32 i = 0; i < indices.size(); i++) {
        this->benchmarkData->indices[i] = indices[i];
    }
}

Memory::InitData* Memory::getInitData() {
    return initData;
}

void Memory::awaitDataConsumed() {
    sem_wait(semDataConsumed);
}

void Memory::postDataAvailable() {
    sem_post(semDataAvailable);
}

void Memory::setBatchSize(i32 size) {
    batchData->header.batchSize = size;
}

void Memory::setMinPathIndex(i32 index) {
    batchData->header.minPathIndex = index;
}

u16& Memory::operator[](u32 n) {
    return batchData->indices[n];
}

void Memory::newBatch() {
    pathCount = 0;
    index = 0;
}

bool Memory::nextPath() {
    return ++pathCount <= maxPaths;
}

void Memory::setNextPathIndex(u16 cityIndex) {
    batchData->indices[index++] = cityIndex;
}
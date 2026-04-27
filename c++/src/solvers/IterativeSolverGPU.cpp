
#include "IterativeSolverGPU.h"

IterativeSolverGPU::IterativeSolverGPU(Memory& memory, std::atomic<bool>& running) : GPUSolver(memory, running) { 

}

int IterativeSolverGPU::solveBenchmark() {
    return 0;
}

int IterativeSolverGPU::solveBatches() {
    return 0;
}
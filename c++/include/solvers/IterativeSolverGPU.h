
#pragma once

#include "GPUSolver.h"

class IterativeSolverGPU : public GPUSolver {
public:
    IterativeSolverGPU(Memory& memory, std::atomic<bool>& running);

    int solveBatches() override;
    int solveBenchmark() override;
};
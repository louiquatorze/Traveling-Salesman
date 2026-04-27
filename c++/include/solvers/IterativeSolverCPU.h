
#pragma once

#include "CPUSolver.h"

class IterativeSolverCPU : public CPUSolver {
public:
    IterativeSolverCPU(Memory& memory, std::atomic<bool>& running);

    int solveBatches() override;
    int solveBenchmark() override;

private:
    void calcFirstBatch();
    void calcNextBatch();

    std::vector<std::vector<f64>> dists;
    std::vector<i32> swaps;

    i32 n, pos;
    f64 minLength;
};

#pragma once

#include "TSSolver.h"

class IterativeSolver : public TSSolver {
public:
    IterativeSolver(Memory& memory, std::atomic<bool>& running);

    void solve() override;

protected:
    void calcNextBatchCPU() override;
    void calcNextBatchGPU() override;

private:
    void calcFirst();

    std::vector<std::vector<f64>> dists;
    std::vector<i32> swaps;

    i32 n;
    f64 minLength;
};
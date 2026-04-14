
#pragma once

#include "TSSolver.h"
#include "../Point.h"

#include <vector>

class IterativeSolver : public TSSolver {
public:
    IterativeSolver(Mode mode, bool gpu);

protected:
    void solveCPU(std::vector<Point>& points) override;
    void solveGPU(std::vector<Point>& points) override;
};
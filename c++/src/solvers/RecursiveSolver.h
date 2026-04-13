
#pragma once

#include "TSSolver.h"
#include "../Point.h"

#include <vector>

class RecursiveSolver : public TSSolver {
public:
    RecursiveSolver(Mode mode, bool gpu);

protected:
    void solveCPU(std::vector<Point>& points) override;
    void solveGPU(std::vector<Point>& points) override;

private:
    std::vector<Point> points;
    std::vector<std::vector<f64>> dists;

    std::pair<std::vector<i32>, f64> RecursiveSolver::solvePath(i32 current, std::vector<i32>& cities, i32 index);
};
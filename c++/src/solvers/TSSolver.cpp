
#include "TSSolver.h"
#include "IterativeSolver.h"

TSSolver::TSSolver(Mode mode, bool gpu) : gpu(gpu), mode(mode) { }

std::unique_ptr<TSSolver> TSSolver::create(Method method, Mode mode, bool gpu) {
    switch (method) {
        case Iterative:
            return std::make_unique<IterativeSolver>(mode, gpu);
    }

    return nullptr;
}

void TSSolver::solve(std::vector<Point>& points) {
    if (points.empty())
        return;
    
    if (gpu) 
        solveGPU(points);
    else  
        solveCPU(points);
}
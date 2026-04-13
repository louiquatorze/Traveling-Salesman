
#pragma once

#include <vector>
#include <functional>  
#include <memory> 

#include "../Point.h"

class TSSolver {
public:
    enum Method {
        Iterative, Ants
    };

    enum Mode {
        Visualize, Benchmark
    };
    
    TSSolver(Mode mode, bool gpu);
    static std::unique_ptr<TSSolver> create(Method method, Mode mode, bool gpu);
    void solve(std::vector<Point>& points);

protected:
    Mode mode;
    
    virtual void solveCPU(std::vector<Point>& points) = 0;
    virtual void solveGPU(std::vector<Point>& points) = 0;

private:
    bool gpu;
};
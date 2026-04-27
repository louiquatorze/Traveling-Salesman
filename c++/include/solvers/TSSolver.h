
#pragma once

#include "Point.h"
#include "Memory.h"

#include <vector>
#include <functional>  
#include <memory>
#include <atomic>

class TSSolver {
public:
    TSSolver(Memory& memory, std::atomic<bool>& running);
    static std::unique_ptr<TSSolver> create(Memory& memory, std::atomic<bool>& running);

    int solve();

protected:
    enum Method {
        Iterative = 0, Recursive, Ants
    };

    Memory& memory;
    std::atomic<bool>& running;

    std::vector<Point> cities;
    bool gpu;
    bool benchmark;
    
    bool solved;
    void writeBatch(std::function<void (void)> calc);
    
    virtual int solveBatches() = 0;
    virtual int solveBenchmark() = 0;
};
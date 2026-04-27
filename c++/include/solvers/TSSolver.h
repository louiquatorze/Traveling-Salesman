
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

    virtual void solve() = 0;
    virtual void print();

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

    std::function<void (void)> calcNextBatch;
    void sendSolved();
    void calcNextBatchWith(std::function<void (void)> calc);
    
    virtual void calcNextBatchCPU() = 0;
    virtual void calcNextBatchGPU() = 0;

private:
    void pickStrategy();
};
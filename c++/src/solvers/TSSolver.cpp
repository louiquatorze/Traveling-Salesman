
#include "TSSolver.h"

#include "IterativeSolverCPU.h"
#include "IterativeSolverGPU.h"

#include <iostream>

TSSolver::TSSolver(Memory& memory, std::atomic<bool>& running) : memory(memory), running(running) {
    Memory::InitData* data = memory.getInitData();
    Point* ptr = data->pts;

    cities = std::vector<Point>(ptr, ptr + data->cityCount);
    gpu = data->gpu;
    benchmark = data->benchmark;   
    
    std::cout << "Cities: " << cities.size() << std::endl;
    std::cout << "GPU: " << gpu << std::endl;
    std::cout << "Benchmark: " << benchmark << std::endl;
    std::cout << "Method: " << data->method << std::endl;
    
    memory.disposeInitData();
}

std::unique_ptr<TSSolver> TSSolver::create(Memory& memory, std::atomic<bool>& running) {
    std::unique_ptr<TSSolver> solver;

    Memory::InitData* initData = memory.getInitData();

    switch ((Method)initData->method) {
        case Iterative:
            if (initData->gpu) 
                solver = std::make_unique<IterativeSolverGPU>(memory, running);
            else
                solver = std::make_unique<IterativeSolverCPU>(memory, running);
            
            break;
        default:
            solver = nullptr;
            std::cerr << "Method not supported" << std::endl;
            break;
    }

    if (solver == nullptr) {
        std::cerr << "Failed to create solver" << std::endl;
        exit(EXIT_FAILURE);
    }
    
    return solver;
}

int TSSolver::solve() {
    if (benchmark) 
        return solveBenchmark();
    else
        return solveBatches();
}

void TSSolver::writeBatch(std::function<void (void)> calc) {
    memory.awaitDataConsumed();

    if (!running)
        return;
        
    memory.newBatch();
    calc();
    memory.postDataAvailable();
}

#include "TSSolver.h"
#include "IterativeSolver.h"

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
    std::unique_ptr<TSSolver> solver = nullptr;

    switch ((Method)memory.getInitData()->method) {
        case Iterative:
            solver = std::make_unique<IterativeSolver>(memory, running);
            break;
    }

    if (solver == nullptr) {
        std::cerr << "Couldn't create appropriate solver" << std::endl;
        exit(EXIT_FAILURE);
    }
    
    solver->pickStrategy();
    
    return solver;
}

void TSSolver::sendSolved() {
    memory.awaitDataConsumed();
    memory.setBatchSize(0);
    memory.postDataAvailable();
}

void TSSolver::calcNextBatchWith(std::function<void (void)> calcNextBatch) {
    memory.awaitDataConsumed();

    if (!running)
        return;
        
    memory.newBatch();
    
    calcNextBatch();

    memory.postDataAvailable();
}

void TSSolver::print() {
    std::cout << cities.size() << " cities: " << std::endl;

    for (Point p : cities) {
        std::cout << p.x << " " << p.y << std::endl;
    }
}

void TSSolver::pickStrategy() {
    if (gpu)
        calcNextBatch = [this]() { calcNextBatchGPU(); };
    else
        calcNextBatch = [this]() { calcNextBatchCPU(); };
}

#include "IterativeSolverCPU.h"

#include "../Point.h"
#include "../Types.h"
#include "../Util.h"

#include <vector>
#include <numeric>
#include <algorithm>
#include <iostream>

IterativeSolverCPU::IterativeSolverCPU(Memory& memory, std::atomic<bool>& running) : CPUSolver(memory, running) { 
    n = cities.size() - 1;        
    dists = Util::calcDistances(cities);
    
    if (!benchmark) {
        for (i32 i = 0; i < n; i++) {
            memory[i] = i + 1;
        }
        memory.setBatchSize(1);
        pos = 1;
    }

    swaps = std::vector<i32>(n, 0);
}

int IterativeSolverCPU::solveBenchmark() {
    f64 minLength = 0.0;   

    std::vector<u16> indices(n);
    std::vector<u16> minIndices(n);

    indices[0] = 1;
    minIndices[0] = 1;

    for (i32 i = 1; i < n; i++) {
        indices[i] = i + 1;
        minIndices[i] = i + 1;
        
        minLength += dists[indices[i - 1]][indices[i]];
    }

    minLength += dists[0][indices[0]];
    minLength += dists[0][indices[n - 1]];

    // Heaps algorithm

    pos = 1;
    while (pos < n) {
        if (swaps[pos] < pos) {
            if (pos % 2 == 0) {
                std::swap(indices[0], indices[pos]);
            } else {
                std::swap(indices[swaps[pos]], indices[pos]);
            }

            f64 length = 0.0;

            for (i32 i = 0; i < n - 1; i++) {
                length += dists[indices[i]][indices[i + 1]];
            }
            
            length += dists[0][indices[0]];
            length += dists[0][indices[n - 1]];
            
            if (length < minLength) {
                minLength = length;
                
                for (i32 i = 0; i < n; i++)
                    minIndices[i] = indices[i];
            }

            swaps[pos]++; 
            pos = 1;
        } else {
            swaps[pos] = 0;
            pos++;
        }
    }

    memory.setBenchmarkDataIndices(minIndices);
    memory.postDataAvailable();
    
    return 0;
}

int IterativeSolverCPU::solveBatches() {
    solved = false;
    
    writeBatch([this]() { calcFirstBatch(); });
    
    while (running && !solved) {
        writeBatch([this]() { calcNextBatch(); });
    }
    
    if (running) {
        memory.awaitDataConsumed();
        memory.setBatchSize(0);
        memory.postDataAvailable();
    }

    return solved ? 0 : 9;
}

void IterativeSolverCPU::calcFirstBatch() {
    f64 length = 0.0;   

    for (i32 i = 1; i < n; i++) {
        length += dists[memory[i - 1]][memory[i]];
    }

    length += dists[0][memory[0]];
    length += dists[0][memory[n - 1]];

    memory.setMinPathIndex(0);
    minLength = length; 
    
    if (n <= 2) {
        solved = true;
    }
}

void IterativeSolverCPU::calcNextBatch() {
    if (pos == n) {
        solved = true;
        return;
    }

    if (swaps[pos] < pos) {
        if (pos % 2 == 0) {
            std::swap(memory[0], memory[pos]);
        } else {
            std::swap(memory[swaps[pos]], memory[pos]);
        }
        
        f64 length = 0.0;
        
        for (i32 i = 0; i < n - 1; i++) {
            length += dists[memory[i]][memory[i + 1]];
        }
        
        length += dists[0][memory[0]];
        length += dists[0][memory[n - 1]];
    
        if (length < minLength) {
            memory.setMinPathIndex(0);
            minLength = length;
        } else {
            memory.setMinPathIndex(-1);
        }

        swaps[pos]++; 
        pos = 1;
    } else {
        swaps[pos] = 0;
        pos++;
    }
}
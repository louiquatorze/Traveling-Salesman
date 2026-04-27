
#include "IterativeSolver.h"
#include "../Point.h"
#include "../Types.h"
#include "../Util.h"

#include <vector>
#include <numeric>
#include <algorithm>
#include <iostream>

IterativeSolver::IterativeSolver(Memory& memory, std::atomic<bool>& running) : TSSolver(memory, running) { 
    n = cities.size() - 1;        
    dists = Util::calcDistances(cities);
    
    for (i16 i = 0; i < n; i++) {
        memory[i] = i + 1;
    }

    memory.setBatchSize(1);

    swaps = std::vector<i32>(n, 0);
}

void IterativeSolver::solve() {
    if (cities.empty())
        return;
    
    solved = false;

    calcNextBatchWith([this]() {
        calcFirst();
    });
    
    while (running && !solved) {
        calcNextBatchWith(calcNextBatch);
    }
    
    if (running)
        sendSolved();
}

void IterativeSolver::calcFirst() {
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

void IterativeSolver::calcNextBatchCPU() {
    i32 pos = 1;

    while (pos < n) {
        std::swap(memory[pos - 1], memory[pos]);
        swaps[pos]++;
        
        if (swaps[pos] <= pos)
            break;

        swaps[pos] = 0;
        pos++;
    }

    if (pos == n) {
        solved = true;
        return;
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
}

void IterativeSolver::calcNextBatchGPU() {
    
}
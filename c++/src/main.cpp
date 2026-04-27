
#include <iostream>

#include "Memory.h"
#include "TSSolver.h"
#include "Point.h"

#include <thread>
#include <chrono>
#include <csignal>
#include <atomic>

/*
Solves a given traveling salesman problem in a given way

args: 
    program
    shm name
    shm size
    sem init name
    sem data available name
    sem data consumed name
*/

std::atomic<bool> running { true };

void handleSignal(int signum) {
    running = false;
}

int main(int argc, char* argv[]) {
    if (argc != 6) {
        std::cerr << "Wrong number of arguments" << std::endl;
        exit(EXIT_FAILURE);
    }

    struct sigaction sa;
    sa.sa_handler = handleSignal;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;

    sigaction(SIGTERM, &sa, nullptr);
    sigaction(SIGINT, &sa, nullptr);

    Memory memory(argv + 1);
    memory.awaitInitData();

    auto solver = TSSolver::create(memory, running);
    return solver->solve();
}
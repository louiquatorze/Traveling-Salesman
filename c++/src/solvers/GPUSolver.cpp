
#include "GPUSolver.h"

GPUSolver::GPUSolver(Memory& memory, std::atomic<bool>& running) : TSSolver(memory, running) { }

GPUSolver::~GPUSolver() { }
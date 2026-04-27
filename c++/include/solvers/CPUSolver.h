
#pragma oncwe

#include "TSSolver.h"

class CPUSolver : public TSSolver {
public:
    CPUSolver(Memory& memory, std::atomic<bool>& running);

protected:
    virtual int solveBatches() = 0;
    virtual int solveBenchmark() = 0;
};

#pragma oncwe

#include "TSSolver.h"

class GPUSolver : public TSSolver {
public:
    GPUSolver(Memory& memory, std::atomic<bool>& running);
    ~GPUSolver();

protected:
    virtual int solveBatches() = 0;
    virtual int solveBenchmark() = 0;
};
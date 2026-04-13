
#include "IterativeSolver.h"
#include "../Point.h"
#include "../Types.h"
#include "../Util.h"

#include <vector>
#include <numeric>
#include <algorithm>

IterativeSolver::IterativeSolver(Mode mode, bool gpu) : TSSolver(mode, gpu) { }

void IterativeSolver::solveCPU(std::vector<Point>& points) {
    i32 n = points.size() + 1;

    bool visualize = mode == Visualize;

    std::vector<std::vector<f64>> dists = Util::calcDistances(points);

    std::vector<i32> cities(n);
    std::iota(cities.begin(), cities.end(), 0);
    cities[n - 1] = 0;

    std::vector<i32> swaps(n, 0);
    
    f64 minLength = 0.0;
    std::vector<i32> minPath(n);

    for (i32 i = 0; i < n - 1; i++) {
        minLength += dists[cities[i]][cities[i + 1]];
        minPath[i] = cities[i];
    }
    minPath[n - 1] = cities[n - 1];

    i32 pos = 2;
    while (pos < n - 1) {
        std::swap(cities[pos], cities[pos - 1]);

        if (++swaps[pos] < pos) {
            f64 length = 0.0;
            
            for (i32 i = 0; i < n - 1; i++)
                length += dists[cities[i]][cities[i + 1]];

            if (length < minLength) {
                minLength = length;
                minPath = cities;
            }

            if (visualize) {
                // Pipe to python
            }
            
            pos = 2;
        } else {
            swaps[pos] = 0;
            pos++;
        }
    }

    std::vector<Point> sorted(n);

    for (i32 i = 0; i < n; i++)
        sorted[i] = points[minPath[i]];
    
    points = sorted;
}

void IterativeSolver::solveGPU(std::vector<Point>& points) {
    
}
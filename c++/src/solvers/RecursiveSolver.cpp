
#include "RecursiveSolver.h"
#include "../Point.h"
#include "../Types.h"
#include "../Util.h"

#include <vector>
#include <numeric>

RecursiveSolver::RecursiveSolver(Mode mode, bool gpu) : TSSolver(mode, gpu) { }

void RecursiveSolver::solveCPU(std::vector<Point>& points) {
    i32 n = points.size();

    if (n == 0)
        return;

    this->points = points;
    dists = Util::calcDistances(points);

    std::vector<i32> not_visited(n - 1);
    std::iota(not_visited.begin(), not_visited.end(), 1);

    auto [path, length] = solvePath(0, not_visited, 1);
}

std::pair<std::vector<i32>, f64> RecursiveSolver::solvePath(i32 current, std::vector<i32>& cities, i32 index) {
    if (index == cities.size()) {
        return { {}, 0 };
    }
    
    auto [minPath, minLength] = solvePath(index, cities, index + 1);
    minLength += dists[current][cities[index]];

    for (int i = index + 1; i < cities.size(); i++) {
        std::swap(cities[index], cities[i]);

        auto [path, length] = solvePath(i, cities, index + 1);
        length += dists[current][cities[i]];
        
        if (length < minLength) {
            minPath = path;
            minLength = length;
        }

        std::swap(cities[index], cities[i]);
    }

    minPath.push_back(current);
    return { minPath, minLength };
}

void RecursiveSolver::solveGPU(std::vector<Point>& points) {
    
}
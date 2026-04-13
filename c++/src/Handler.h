
#pragma once

#include <vector>
#include <string>
#include <optional>

#include "Point.h"
#include "solvers/TSSolver.h"

class Handler {
public:
    Handler();
    ~Handler();
    void handle();

private:
    std::vector<Point> readInput();
    std::optional<Point> parseLine(std::string& line);
};
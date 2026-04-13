
#pragma once

#include "Types.h"
#include "Point.h"

#include <vector>

class Util {
public:
    static std::vector<std::vector<f64>> calcDistances(std::vector<Point>& points);
    static f64 calcDistance(Point& p1, Point& p2);
    static u64 factorial(u32 n);
};
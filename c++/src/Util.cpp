
#include "Util.h"

#include <cmath>

std::vector<std::vector<f64>> Util::calcDistances(std::vector<Point>& points) {
    int n = points.size();

    std::vector<std::vector<f64>> dists(n, std::vector<f64>(n));

    for (int i = 0; i < n - 1; i++) {
        dists[i][i] = 0;

        for (int j = i + 1; j < n; j++) {
            f64 dist =  calcDistance(points[i], points[j]);
            dists[i][j] = dists[j][i] = dist;
        }
    }

    return dists;
}

f64 Util::calcDistance(Point& p1, Point& p2) {
    f64 dx = p1.x - p2.x;
    f64 dy = p1.y - p2.y;

    return sqrt(dx*dx + dy*dy);
}

u64 Util::factorial(u32 n) {
    u64 val = 1;

    while (n > 0)
        val *= n--;

    return val;
}
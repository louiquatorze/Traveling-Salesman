
#include "Handler.h"

#include <iostream>
#include <string>
#include <optional>
#include <stdexcept>
#include <memory>

Handler::Handler() {

}

Handler::~Handler() {

}

void Handler::handle() {
    std::string line;

    std::vector pts = readInput();

    std::unique_ptr<TSSolver> solver = TSSolver::create(TSSolver::Iterative, TSSolver::Benchmark, false);
    solver->solve(pts);

    for (Point p : pts)
        std::cout << p.x << " " << p.y << "\n";
    
    std::cout.flush();
}

std::vector<Point> Handler::readInput() {
    std::string line;
    std::vector<Point> pts = {};

    while (std::getline(std::cin, line) && line != "~") {
        std::optional<Point> p = parseLine(line);
        
        if (p.has_value())
            pts.push_back(p.value());
    }

    return pts;
}

std::optional<Point> Handler::parseLine(std::string& line) {
    int delim = line.find(' ');

    if (delim == std::string::npos) {
        std::cerr << "Input point is not valid" << std::endl;
        return std::nullopt;
    }

    Point p;

    try {
        p.x = std::stod(line.substr(0, delim));
        p.y = std::stod(line.substr(delim + 1));
    } catch (const std::invalid_argument& e) {
        std::cerr << "Input number is invalid: " << e.what() << std::endl;
        return std::nullopt;
    }

    return std::optional(p);
}
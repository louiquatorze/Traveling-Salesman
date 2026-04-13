
cmake_minimum_required(VERSION 3.16)
project(travelingSalesman LANGUAGES C CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_executable(travelingSalesman 
    src/main.cpp 
    src/Handler.cpp
    src/Util.cpp
    src/solvers/TSSolver.cpp
    src/solvers/IterativeSolver.cpp
)
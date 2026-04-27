
cmake_minimum_required(VERSION 3.16)
project(travelingSalesman LANGUAGES C CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_executable(travelingSalesman 
    src/main.cpp 
    src/Util.cpp
    src/Memory.cpp
    src/solvers/TSSolver.cpp
    src/solvers/CPUSolver.cpp
    src/solvers/GPUSolver.cpp
    src/solvers/IterativeSolverCPU.cpp
    src/solvers/IterativeSolverGPU.cpp
    src/solvers/
)

target_include_directories(travelingSalesman PUBLIC 
    include
    include/solvers
)

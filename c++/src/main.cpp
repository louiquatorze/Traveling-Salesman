
#include <iostream>

#include "Handler.h"

int main() {
    Handler handler;

    while (std::cin.peek() != 'q') {
        handler.handle();
    }

    return 0;
}
#include <cuda/version>

#include <iostream>

int main() {
    std::cout << "CCCL version: " <<
        CCCL_MAJOR_VERSION << "." <<
        CCCL_MINOR_VERSION << "." <<
        CCCL_PATCH_VERSION << std::endl;
}

cmake_minimum_required(VERSION 3.5)

# http://stackoverflow.com/questions/9160335/os-specific-instructions-in-cmake-how-to
# https://cmake.org/Wiki/CMake_Useful_Variables

if (WIN32)
    execute_process(COMMAND bash ./build/linux/Makefile)
endif (WIN32)

if (UNIX)
    execute_process(COMMAND bash ./build/win32/Makefile)
endif (UNIX)


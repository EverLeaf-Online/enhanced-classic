cmake_minimum_required(VERSION 3.20)
project(everleaf_custom_wz_builder LANGUAGES CXX C)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT DEFINED LIBWZ_SOURCE_DIR OR LIBWZ_SOURCE_DIR STREQUAL "")
    message(FATAL_ERROR "LIBWZ_SOURCE_DIR must point to the pinned libwz checkout")
endif()

set(BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(BUILD_CAPI OFF CACHE BOOL "" FORCE)
set(BUILD_JNI OFF CACHE BOOL "" FORCE)
set(BUILD_WASM OFF CACHE BOOL "" FORCE)
add_subdirectory("${LIBWZ_SOURCE_DIR}" "${CMAKE_BINARY_DIR}/libwz" EXCLUDE_FROM_ALL)

add_executable(everleaf-custom-wz-builder main.cpp)
target_link_libraries(everleaf-custom-wz-builder PRIVATE wz)

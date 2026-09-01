cmake_minimum_required(VERSION 3.20)
project(everleaf_evan_wz_patcher LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT DEFINED LIBWZ_SOURCE)
  message(FATAL_ERROR "LIBWZ_SOURCE must point to the pinned libwz checkout")
endif()

add_subdirectory("${LIBWZ_SOURCE}" "${CMAKE_BINARY_DIR}/libwz")

add_executable(everleaf-evan-wz-patcher main.cpp)
target_link_libraries(everleaf-evan-wz-patcher PRIVATE wz)

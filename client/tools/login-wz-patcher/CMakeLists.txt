cmake_minimum_required(VERSION 3.20)
project(everleaf_login_wz_patcher LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT DEFINED LIBWZ_SOURCE)
  message(FATAL_ERROR "LIBWZ_SOURCE must point to the pinned libwz source checkout")
endif()

add_subdirectory("${LIBWZ_SOURCE}" "${CMAKE_BINARY_DIR}/libwz" EXCLUDE_FROM_ALL)

add_executable(everleaf-login-wz-patcher main.cpp)
target_link_libraries(everleaf-login-wz-patcher PRIVATE wz)

add_executable(everleaf-remove-map-login-frame remove-map-login-frame.cpp)
target_link_libraries(everleaf-remove-map-login-frame PRIVATE wz)

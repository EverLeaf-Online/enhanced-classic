cmake_minimum_required(VERSION 3.20)
project(everleaf_evan_xml_donor_builder LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT DEFINED LIBWZ_SOURCE)
  message(FATAL_ERROR "LIBWZ_SOURCE must point to the pinned libwz checkout")
endif()

include(FetchContent)
FetchContent_Declare(
  pugixml
  GIT_REPOSITORY https://github.com/zeux/pugixml.git
  GIT_TAG ee86beb30e4973f5feffe3ce63bfa4fbadf72f38
  GIT_SHALLOW FALSE
)
FetchContent_MakeAvailable(pugixml)

add_subdirectory("${LIBWZ_SOURCE}" "${CMAKE_BINARY_DIR}/libwz")

add_executable(everleaf-evan-xml-donor-builder main.cpp)
target_precompile_headers(everleaf-evan-xml-donor-builder PRIVATE <algorithm> <array>)
if(MSVC)
  target_compile_options(everleaf-evan-xml-donor-builder PRIVATE /EHsc)
else()
  target_compile_options(everleaf-evan-xml-donor-builder PRIVATE -fexceptions)
endif()
target_link_libraries(everleaf-evan-xml-donor-builder PRIVATE wz pugixml::pugixml)

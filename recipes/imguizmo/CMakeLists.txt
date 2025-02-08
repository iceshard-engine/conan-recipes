cmake_minimum_required(VERSION 3.15)
project(imguizmo CXX)

find_package(imgui)

add_library(imguizmo
    ImGuizmo.cpp
)

target_link_libraries(imguizmo imgui::imgui)

install(DIRECTORY "${CMAKE_SOURCE_DIR}"
    DESTINATION "include/imguizmo"
    FILES_MATCHING PATTERN "*.h"
)

install(TARGETS imguizmo)

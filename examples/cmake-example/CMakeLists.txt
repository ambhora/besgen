cmake_minimum_required(VERSION 3.25)
project(cmake-example VERSION 0.1.0 LANGUAGES CXX Fortran)

find_package(besa CONFIG REQUIRED)
include(cmake/features.cmake)
include(cmake/external.cmake)

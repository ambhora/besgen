# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 besgen developers
# --------------------------------------------------------------------------------------------------
cmake_minimum_required(VERSION 4.3)
project(cmake-example VERSION 0.1.0 LANGUAGES CXX Fortran)

find_package(besa CONFIG REQUIRED)
include(cmake/options.cmake)
include(cmake/external.cmake)
include(CTest)
if(BUILD_SOURCE)
  besa_add_subdirectory(DIRECTORY src/cpp TYPE cpp)
endif()
if(BUILD_TESTING)
  add_subdirectory(test)
endif()

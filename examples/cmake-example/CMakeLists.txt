# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 besgen developers
# --------------------------------------------------------------------------------------------------
cmake_minimum_required(VERSION 4.3)
project(cmake-example VERSION 0.1.0 LANGUAGES NONE)

find_package(besa CONFIG REQUIRED)
include(cmake/options.cmake)
include(cmake/external.cmake)
include(CTest)
if(BUILD_SOURCE)
  add_subdirectory(src)
endif()
if(BUILD_TESTING)
  add_subdirectory(test)
endif()

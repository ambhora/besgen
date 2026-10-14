# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 cmake-example developers
# --------------------------------------------------------------------------------------------------
# Define the project library and attach its implementation directories.
besa_add_library(NAME libcmake-example INSTALL YES)

besa_add_directory(LIBRARY libcmake-example ROOT "${CMAKE_CURRENT_SOURCE_DIR}/cpp" TYPE cpp)
besa_add_directory(LIBRARY libcmake-example ROOT "${CMAKE_CURRENT_SOURCE_DIR}/fortran" TYPE fortran)

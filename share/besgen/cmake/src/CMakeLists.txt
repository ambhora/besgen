# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 __PROJECT__ developers
# --------------------------------------------------------------------------------------------------
# Define the project library and attach its implementation directories.
besa_add_library(NAME lib__PROJECT__ INSTALL YES)

besa_add_directory(LIBRARY lib__PROJECT__ ROOT "${CMAKE_CURRENT_SOURCE_DIR}/cpp" TYPE cpp)

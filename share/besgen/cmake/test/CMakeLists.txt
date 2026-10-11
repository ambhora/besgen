# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 __PROJECT__ developers
# --------------------------------------------------------------------------------------------------
find_package(Catch2 3 CONFIG REQUIRED)

besa_add_library(
  NAME libtest__PROJECT__
  TYPE STATIC
  INSTALL FALSE
  SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/lib/test__MODULE__.cpp"
  PUBLIC_INCLUDE_DIRECTORIES "${CMAKE_CURRENT_SOURCE_DIR}/include"
)

besa_test_add_directory(
  NAME unit
  PREFIX __PROJECT__
  TARGET_LIST __PROJECT__::libtest__PROJECT__ Catch2::Catch2WithMain
  LABELS unit
)

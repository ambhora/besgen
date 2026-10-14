# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 __PROJECT__ developers
# --------------------------------------------------------------------------------------------------
find_package(Catch2 3 CONFIG REQUIRED)

# This library belongs only to the test suite; production sources are optional.
besa_add_library(NAME libtest__PROJECT__ TYPE STATIC INSTALL NO)
besa_add_directory(LIBRARY libtest__PROJECT__ ROOT "${CMAKE_CURRENT_SOURCE_DIR}" TYPE cpp)

besa_test_add_directory(
  NAME unit
  PREFIX __PROJECT__
  TARGET_LIST __PROJECT__::libtest__PROJECT__ Catch2::Catch2WithMain
  LABELS unit
)

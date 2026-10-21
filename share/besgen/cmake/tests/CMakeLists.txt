# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 __PROJECT__ developers
# --------------------------------------------------------------------------------------------------
# Test support is a separate, non-installed library and needs no production sources.
besa_add_library(NAME libtest__PROJECT__ TYPE STATIC INSTALL NO)
target_link_libraries(libtest__PROJECT__ PUBLIC Catch2::Catch2WithMain)
add_subdirectory(common)

besa_test_add_directory(
  NAME unit
  PREFIX __PROJECT__
  TARGET_LIST __PROJECT__::libtest__PROJECT__
  LABELS unit
  COVERAGE_GROUP unit
)

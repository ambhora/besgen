// --------------------------------------------------------------------------------------------------
// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2026 __PROJECT__ developers
// --------------------------------------------------------------------------------------------------
#include <test__MODULE__/kernels.hpp>
#include <catch2/catch_test_macros.hpp>

TEST_CASE("test library can be used independently of production sources") {
  REQUIRE(__MODULE__::test::smoke() == 42);
}

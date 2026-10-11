<!--
--------------------------------------------------------------------------------------------------
SPDX-License-Identifier: Apache-2.0
SPDX-FileCopyrightText: 2026 __PROJECT__ developers
--------------------------------------------------------------------------------------------------
-->
# C++ modules

Add public C++20 module interface files (`*.cppm`) here. BESA discovers them
recursively and attaches them to `lib__PROJECT__` as a CMake `CXX_MODULES` file set.
There is no separate module library, compatibility wrapper, or additional CMake setup.

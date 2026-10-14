<!--
--------------------------------------------------------------------------------------------------
SPDX-License-Identifier: Apache-2.0
SPDX-FileCopyrightText: 2026 __PROJECT__ developers
--------------------------------------------------------------------------------------------------
-->
# C++ implementation layout

Put C++ implementation files under `lib/` and public headers under `include/`.
To use C++ modules, create `module/` and place **only C++ module interface
source files** there. Besa adds every file in `module/` to the CMake
`CXX_MODULES` file set, including files with unconventional extensions, so do
not store README or other documentation files in that directory.

Select the C++ standard and compiler through a CMake preset, toolchain file, or
configure-time options, not project `CMakeLists.txt` settings.

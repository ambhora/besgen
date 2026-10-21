#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 __PROJECT__ developers
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail
: "${CXX:?Set CXX to select a compiler}"
: "${CC:?Set CC to select a compiler}"
if [[ -n "${__MODULE_UPPER___TOOLSET_ENV:-}" ]]; then
  # shellcheck disable=SC1090
  source "${__MODULE_UPPER___TOOLSET_ENV}"
fi
if [[ -n "${__MODULE_UPPER___DEPS_ENV:-}" ]]; then
  : "${SPACK_ROOT:?Spack must be bootstrapped to use its environment}"
  # shellcheck source=/dev/null
  source "${SPACK_ROOT}/share/spack/setup-env.sh"
  spack env activate "${__MODULE_UPPER___DEPS_ENV}"
fi
"${CXX}" --version
cmake --preset ci
cmake --build --preset ci --parallel
ctest --preset ci --no-tests=error

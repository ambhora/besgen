# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 besgen developers
# --------------------------------------------------------------------------------------------------
# External dependencies.

besa_dependency_add(
  NAME MPI
  CONDITION "mpi"
)

besa_dependency_add(
  NAME HDF5
  VERSION "1.14"
  CONDITION "mpi"
)

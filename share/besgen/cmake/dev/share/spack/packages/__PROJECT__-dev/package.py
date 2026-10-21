# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 __PROJECT__ developers
# --------------------------------------------------------------------------------------------------
from spack.package import *


class __PROJECT_CLASS__Dev(BundlePackage):
    """Development tools and test dependencies for __PROJECT__."""

    version("1.1")

    variant("test", default=False, description="Install test dependencies")

    # Build tools are available in the environment view on developer machines and CI.
    depends_on("cmake@4.3:", type=("build", "run"))
    depends_on("ninja", type=("build", "run"))
    depends_on("catch2@3:", when="+test", type=("link", "run"))

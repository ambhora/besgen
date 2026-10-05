from spack.package import *


class __PROJECT_CLASS__Dev(BundlePackage):
    """Development environment for __PROJECT__."""

    version("1.0")

    variant("test", default=False, description="Install test dependencies")

    depends_on("besa")
    depends_on("catch2", when="+test")

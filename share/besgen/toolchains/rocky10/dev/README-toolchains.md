# Managed Rocky Linux 10 development toolchains

This optional besgen profile uses an x86-64-v3 Spack installation in a Rocky Linux 10
container. The default CI job uses system GCC 14 and builds development dependencies
with Spack. Pinned compiler roots are deliberately **not** assumed to exist.

Configure `dev/etc/toolchains.toml` (especially the OCI image and compiler root
selectors), then run `uv run --project dev __PROJECT__-dev compiler sync`.
Building cached compiler roots requires `compiler build`, `compiler push`, and
committing `dev/compilers/spack.lock` before cache-only restore can succeed.

Each selected compiler gets a separate concretized dependency environment under
`dev/.spack-matrix/`; those locks should not be mixed between compiler selectors.
`deps install --compiler GCC:14` works without a separate compiler cache and
is the initial CI workflow. The bootstrap container workflow can be enabled
when the image destination is configured for your GitHub registry.

BESA is vendored independently and is not modified by this infrastructure.

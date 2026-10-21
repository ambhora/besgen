# SPDX-FileCopyrightText: 2026 __PROJECT__ developers
# SPDX-License-Identifier: Apache-2.0
FROM rockylinux/rockylinux:10

# Reuse the same bootstrap logic that desktop and GitHub Actions execute.
# Copy only the stdlib bootstrap and its declarative configuration.
WORKDIR /opt/__PROJECT__/bootstrap
COPY dev/etc/toolchains.toml dev/etc/toolchains.toml
COPY dev/src/__DEV_MODULE__/toolchains.py dev/src/__DEV_MODULE__/toolchains.py
RUN __MODULE_UPPER___BUILD_BOOTSTRAP_IMAGE=1 python3 dev/src/__DEV_MODULE__/toolchains.py --backend native bootstrap \
 && touch /opt/__PROJECT__/.bootstrap-ready \
 && /opt/__PROJECT__/spack-src/bin/spack --version

ENV SPACK_ROOT=/opt/__PROJECT__/spack-src \
    SPACK_DISABLE_LOCAL_CONFIG=1 \
    PATH=/opt/__PROJECT__/spack-src/bin:${PATH}
WORKDIR /workspace

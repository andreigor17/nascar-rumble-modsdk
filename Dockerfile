FROM rust:1.74.1-slim-bookworm@sha256:53596c66027523b2289c6e7c96bff119416be22d2cf52734b4962e13371c54cf AS rust-toolchain

FROM python:3.14.0-slim-bookworm@sha256:d13fa0424035d290decef3d575cea23d1b7d5952cdf429df8f5542c71e961576 AS ci-base

RUN apt-get update \
    && apt-get install --yes --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

FROM ci-base AS public-ci

COPY . .

CMD ["make", "ci-public"]

FROM ci-base AS matching-toolchain

ARG BINUTILS_VERSION=2.47
ARG BINUTILS_SHA256=3068128c75cda9f898ccb4211d360246e8e195ffcc9dfb655b23ae23a54800e8

RUN apt-get update \
    && apt-get install --yes --no-install-recommends build-essential ca-certificates curl file \
    && rm -rf /var/lib/apt/lists/*

RUN curl --fail --location --silent --show-error --retry 3 \
       "https://sourceware.org/pub/binutils/releases/binutils-${BINUTILS_VERSION}.tar.bz2" \
       --output /tmp/binutils.tar.bz2 \
    && echo "${BINUTILS_SHA256}  /tmp/binutils.tar.bz2" | sha256sum --check --strict \
    && tar --extract --bzip2 --file /tmp/binutils.tar.bz2 --directory /tmp \
    && mkdir /tmp/binutils-build \
    && cd /tmp/binutils-build \
    && CFLAGS="-O0 -g0" CXXFLAGS="-O0 -g0" \
       "/tmp/binutils-${BINUTILS_VERSION}/configure" \
       --target=mipsel-linux-gnu --disable-nls --disable-werror --disable-gdb --disable-sim \
    && make --jobs=1 all-gas all-ld all-binutils \
    && make install-gas install-ld install-binutils \
    && mipsel-linux-gnu-as --version | head -1 | grep -F "${BINUTILS_VERSION}" \
    && command -v mipsel-linux-gnu-ld mipsel-linux-gnu-objcopy \
    && rm -rf /tmp/binutils*

FROM matching-toolchain AS matching-python

COPY --from=rust-toolchain /usr/local/cargo /usr/local/cargo
COPY --from=rust-toolchain /usr/local/rustup /usr/local/rustup

ENV CARGO_HOME=/usr/local/cargo \
    RUSTUP_HOME=/usr/local/rustup \
    PATH=/usr/local/cargo/bin:$PATH

COPY Makefile requirements-splat.lock ./

RUN make setup-ci-deps

FROM matching-python AS matching-setup

COPY config/decomp_tools.lock.json config/decomp_tools.lock.json
COPY scripts/setup_decomp_tools.py scripts/setup_decomp_tools.py

RUN python3 scripts/setup_decomp_tools.py

FROM matching-toolchain AS matching-ci

COPY . .
COPY --from=matching-python /workspace/.venv /workspace/.venv
COPY --from=matching-setup /workspace/tools /workspace/tools

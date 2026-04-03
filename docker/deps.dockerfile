FROM quay.io/pypa/manylinux_2_28_x86_64:latest as deps

COPY scripts/build_deps.sh  /tmp/build_deps.sh
COPY scripts/deps/          /tmp/deps/
RUN bash /tmp/build_deps.sh

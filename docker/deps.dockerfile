FROM quay.io/pypa/manylinux_2_28_x86_64:latest

COPY scripts/build_deps.sh /tmp/build_deps.sh
RUN bash /tmp/build_deps.sh

FROM quay.io/pypa/manylinux_2_28_x86_64

ENV PATH="/opt/python/cp311-cp311/bin:${PATH}"

COPY scripts/build_deps.sh /tmp/build_deps.sh
RUN chmod +x /tmp/build_deps.sh

RUN /tmp/build_deps.sh
RUN rm /tmp/build_deps.sh

COPY . /project
WORKDIR /project

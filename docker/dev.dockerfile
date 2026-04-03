FROM quay.io/pypa/manylinux_2_28_x86_64:latest AS deps

COPY scripts/build_deps.sh  /tmp/build_deps.sh
COPY scripts/deps/          /tmp/deps/
RUN bash /tmp/build_deps.sh

FROM deps AS dev

ENV PYBIN=/opt/python/cp312-cp312/bin
ENV PATH="${PYBIN}:${PATH}"

COPY scripts/build_editor.sh  /tmp/build_editor.sh
RUN bash /tmp/build_editor.sh

RUN ln -sf ${PYBIN}/python /usr/local/bin/python && \
    ln -sf ${PYBIN}/pip    /usr/local/bin/pip

WORKDIR /workspace
CMD ["/bin/bash"]

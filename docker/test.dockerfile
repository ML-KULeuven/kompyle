FROM quay.io/pypa/manylinux_2_28_x86_64:latest AS deps

COPY scripts/build_deps.sh /tmp/build_deps.sh
RUN bash /tmp/build_deps.sh

FROM deps AS dev

ENV PYBIN=/opt/python/cp312-cp312/bin
ENV PATH="${PYBIN}:${PATH}"

RUN ${PYBIN}/pip install --upgrade pip

WORKDIR /workspace

RUN ${PYBIN}/pip install \
    scikit-build-core \
    "nanobind>=1.3.2" \
    pytest \
    pytest-xdist \
    torch \
    "pysdd @ git+https://github.com/IbrahimElk/pysdd.git@feat/add-capsule-to-sddnode" \
    "klaycircuits @ git+https://github.com/IbrahimElk/klay.git@feat/sd-dnnf-checker"

RUN ${PYBIN}/pytest tests/

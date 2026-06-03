FROM quay.io/pypa/manylinux_2_28_x86_64:latest AS deps

WORKDIR /tmp

COPY scripts/deps/common.sh             /tmp/deps/common.sh
COPY scripts/deps/00_system.sh          /tmp/deps/00_system.sh
RUN bash /tmp/deps/00_system.sh

COPY scripts/deps/01_boost.sh           /tmp/deps/01_boost.sh
RUN bash /tmp/deps/01_boost.sh

COPY scripts/deps/01_gmp.sh             /tmp/deps/01_gmp.sh
RUN bash /tmp/deps/01_gmp.sh

COPY scripts/deps/02_mpfr.sh            /tmp/deps/02_mpfr.sh
RUN bash /tmp/deps/02_mpfr.sh

COPY scripts/deps/03_flint.sh           /tmp/deps/03_flint.sh
RUN bash /tmp/deps/03_flint.sh

COPY scripts/deps/04_cereal.sh          /tmp/deps/04_cereal.sh
RUN bash /tmp/deps/04_cereal.sh

COPY scripts/deps/05_armadillo.sh       /tmp/deps/05_armadillo.sh
RUN bash /tmp/deps/05_armadillo.sh

COPY scripts/deps/06_ensmallen.sh       /tmp/deps/06_ensmallen.sh
RUN bash /tmp/deps/06_ensmallen.sh

COPY scripts/deps/07_mlpack.sh          /tmp/deps/07_mlpack.sh
RUN bash /tmp/deps/07_mlpack.sh

COPY scripts/deps/08_cadical.sh         /tmp/deps/08_cadical.sh
RUN bash /tmp/deps/08_cadical.sh

COPY scripts/deps/09_cadiback.sh        /tmp/deps/09_cadiback.sh
RUN bash /tmp/deps/09_cadiback.sh

COPY scripts/deps/10_breakid.sh         /tmp/deps/10_breakid.sh
RUN bash /tmp/deps/10_breakid.sh

COPY scripts/deps/11_cryptominisat.sh   /tmp/deps/11_cryptominisat.sh
RUN bash /tmp/deps/11_cryptominisat.sh

COPY scripts/deps/12_sbva.sh            /tmp/deps/12_sbva.sh
RUN bash /tmp/deps/12_sbva.sh

COPY scripts/deps/13_arjun.sh           /tmp/deps/13_arjun.sh
RUN bash /tmp/deps/13_arjun.sh

COPY scripts/deps/14_approxmc.sh        /tmp/deps/14_approxmc.sh
RUN bash /tmp/deps/14_approxmc.sh

COPY scripts/deps/15_ganak.sh           /tmp/deps/15_ganak.sh
RUN bash /tmp/deps/15_ganak.sh

COPY scripts/deps/17_d4v2.sh            /tmp/deps/17_d4v2.sh
RUN bash /tmp/deps/17_d4v2.sh

FROM deps AS dev

ENV PYBIN=/opt/python/cp312-cp312/bin
ENV PATH="${PYBIN}:${PATH}"

COPY scripts/build_editor.sh  /tmp/build_editor.sh
RUN bash /tmp/build_editor.sh

RUN ln -sf ${PYBIN}/python /usr/local/bin/python && \
    ln -sf ${PYBIN}/pip    /usr/local/bin/pip

WORKDIR /workspace

# RUN pip install --upgrade pip wheel scikit-build-core "nanobind>=1.3.2"
# RUN pip install setuptools_scm klaycircuits
# RUN pip wheel . --no-build-isolation -w dist/
# RUN pip install auditwheel
# RUN auditwheel repair dist/kompyle-*.whl -w dist/repaired/ --exclude libklay.so
# RUN pip install dist/repaired/kompyle-*.whl

CMD ["/bin/bash"]

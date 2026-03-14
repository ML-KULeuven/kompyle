FROM quay.io/pypa/manylinux_2_28_x86_64:latest

COPY scripts/build_deps.sh /tmp/build_deps.sh
RUN chmod +x /tmp/build_deps.sh
RUN /tmp/build_deps.sh
RUN rm /tmp/build_deps.sh

COPY . /project
WORKDIR /project

RUN /opt/python/cp310-cp310/bin/pip install . && \
    /opt/python/cp310-cp310/bin/pip install pytest && \
    /opt/python/cp310-cp310/bin/pytest tests/

RUN /opt/python/cp311-cp311/bin/pip install . && \
    /opt/python/cp311-cp311/bin/pip install pytest && \
    /opt/python/cp311-cp311/bin/pytest tests/

RUN /opt/python/cp312-cp312/bin/pip install . && \
    /opt/python/cp312-cp312/bin/pip install pytest && \
    /opt/python/cp312-cp312/bin/pytest tests/

RUN /opt/python/cp310-cp310/bin/pip wheel . -w /wheelhouse
RUN /opt/python/cp311-cp311/bin/pip wheel . -w /wheelhouse
RUN /opt/python/cp312-cp312/bin/pip wheel . -w /wheelhouse

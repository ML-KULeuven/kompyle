# Kompyle

Kompyle is a Python library providing an interface to several d-DNNF knowledge compilers.

---

## Local development

Kompyle depends on many c++ libraries that are not available in standard OS
package managers.  The easiest way to get a working environment on any
platform (windows, macOS, Linux) is via containers.

### Prerequisites

Install a container runtime such as
[Docker Desktop](https://www.docker.com/products/docker-desktop/),
[Docker Engine](https://docs.docker.com/engine/install/), or
[Podman](https://podman.io/getting-started/installation).

### Getting started

```bash
git clone https://github.com/ML-KULeuven/kompyle
cd kompyle

podman-compose build dev
podman-compose up -d dev
podman-compose exec dev bash
```

Inside the container the repo is mounted at `/workspace`, so any edit you
make on the host is immediately visible.

```bash
[root@956fe8c8ad0b workspace]# python -m venv .venv
[root@956fe8c8ad0b workspace]# source .venv/bin/activate
[root@956fe8c8ad0b workspace]# pip install ".[dev]"
[root@956fe8c8ad0b workspace]# pytest tests/
[root@956fe8c8ad0b workspace]# nvim
```

If you prefer to work natively, install the c++ dependencies by following
the script `build_deps.sh`.

## License

Apache 2.0 - see [LICENSE](LICENSE).

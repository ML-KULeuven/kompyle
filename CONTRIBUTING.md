# Contributing

We welcome pull requests from everyone.

## Getting the code

Fork the repository, then clone your fork:

```bash
git clone git@github.com:your-username/kompyle.git
```

## Local development

Kompyle depends on several C++ libraries that are not available in standard
OS package managers. The easiest way to get a working environment on any
platform (Windows, macOS, Linux) is via containers.

## Prerequisites

Install a container runtime such as:
- Docker Desktop: https://www.docker.com/products/docker-desktop/
- Docker Engine: https://docs.docker.com/engine/install/
- Podman: https://podman.io/getting-started/installation

## Getting started

```bash
cd kompyle

podman-compose build dev
podman-compose up -d dev
podman-compose exec dev bash
```

Inside the container, the repository is mounted at `/workspace`, so any
changes you make on the host are immediately visible.

```bash
[root workspace]# python -m venv .venv
[root workspace]# source .venv/bin/activate
[root workspace]# pip install ".[dev]"
[root workspace]# pytest tests/
[root workspace]# nvim
```

If you prefer to work natively, install the C++ dependencies by following
the `build_deps.sh` script.

## Running tests

Make sure the tests pass before and after your changes:

```bash
pytest tests/
```

## Submitting changes

1. Make your changes.
2. Add tests for your changes.
3. Ensure all tests pass.
4. Push to your fork and [submit a pull request][pr].

[pr]: https://github.com/ML-KULeuven/kompyle/compare/

## Guidelines

Follow these guidelines:

- Write tests.
- Follow the Google C++ style guide:
  https://google.github.io/styleguide/cppguide.html
- Follow the Google Python style guide:
  https://google.github.io/styleguide/pyguide.html
- Write good commit messages:
  http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html

## Contributors

- Ibrahim El Kaddouri
- Vincent Derkinderen

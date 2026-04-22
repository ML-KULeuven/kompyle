# Building and installing

```bash
podman build -t kompyle-env -f docker/dev.dockerfile .
podman run --rm -it kompyle-env bash
```

```bash
pip install notebook
jupyter notebook --allow-root --ip=0.0.0.0 --no-browser
```

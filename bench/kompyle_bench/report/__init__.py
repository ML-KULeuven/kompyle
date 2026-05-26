# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Dashboard reporting subsystem.

Three layers:

* `load`       read JSON result files into row dicts.
* `aggregate`  turn rows into chart-ready series.
* `server`     small HTTP server exposing ``/api/...`` + static files.
"""

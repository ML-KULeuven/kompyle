# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Tiny live dashboard server.

Routes:

* ``GET /`` or ``/index.html`` -> ``web/index.html``
* ``GET /static/...``          -> file from ``web/static/``
* ``GET /api/experiments``     -> ``[exp_id, ...]``
* ``GET /api/results?exp_id=N``-> aggregated chart data for experiment N

Result JSON is re-read from disk on every request so a running browser
session picks up new completions when you refresh.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from kompyle_bench.report.aggregate import aggregate
from kompyle_bench.report.load import latest_exp_id, list_exp_ids


_MIME = {
    ".html": "text/html; charset=utf-8",
    ".js":   "application/javascript; charset=utf-8",
    ".mjs":  "application/javascript; charset=utf-8",
    ".css":  "text/css; charset=utf-8",
    ".json": "application/json",
    ".svg":  "image/svg+xml",
    ".png":  "image/png",
    ".ico":  "image/x-icon",
}


def _make_handler(benchmark_dir: Path, web_dir: Path, default_exp_id: int | None):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # pyright:ignore
            pass

        # response helpers

        def _send(self, status: int, content_type: str, body: bytes,
                  cache: bool = False) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            if not cache:
                self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, payload) -> None:
            self._send(200, "application/json", json.dumps(payload).encode())

        def _send_error(self, status: int, msg: str) -> None:
            self._send(status, "text/plain; charset=utf-8", msg.encode())

        # request parsing

        def _exp_id_from_query(self) -> int | None:
            qs = parse_qs(urlparse(self.path).query)
            if "exp_id" in qs:
                return int(qs["exp_id"][0])
            return default_exp_id or latest_exp_id(benchmark_dir)

        def _url_path(self) -> str:
            return urlparse(self.path).path

        # routing

        def do_GET(self):
            path = self._url_path()
            if path in ("/", "/index.html"):
                return self._serve_index()
            if path.startswith("/static/"):
                return self._serve_static(path[len("/static/"):])
            if path == "/api/experiments":
                return self._send_json(list_exp_ids(benchmark_dir))
            if path == "/api/results":
                return self._serve_results()
            self._send_error(404, "not found")

        # route handlers

        def _serve_index(self) -> None:
            self._send(200, _MIME[".html"],
                       (web_dir / "index.html").read_bytes())

        def _serve_static(self, rel: str) -> None:
            target = (web_dir / "static" / rel).resolve()
            static_root = (web_dir / "static").resolve()
            if static_root not in target.parents and target != static_root:
                return self._send_error(403, "forbidden")
            if not target.is_file():
                return self._send_error(404, "not found")
            mime = _MIME.get(target.suffix, "application/octet-stream")
            self._send(200, mime, target.read_bytes(), cache=True)

        def _serve_results(self) -> None:
            eid = self._exp_id_from_query()
            if eid is None:
                return self._send_error(404, "no experiment folders found")
            try:
                data = aggregate(benchmark_dir, eid)
                self._send_json(data)
                print(f"  /api/results → exp{eid:04d}"
                      f"  ({data['n_compile']} compile,"
                      f" {data['n_count']} count,"
                      f" {data['n_infer']} infer,"
                      f" {data['n_experiment']} experiment)")
            except Exception as exc:
                self._send_error(500, str(exc))

    return Handler


def serve(
    *,
    benchmark_dir: Path,
    web_dir: Path,
    port: int,
    exp_id: int | None,
) -> None:
    handler = _make_handler(benchmark_dir, web_dir, exp_id)
    httpd = HTTPServer(("", port), handler)
    desc = f"exp{exp_id:04d}" if exp_id else "latest (auto-detected per request)"
    print(f"Serving at http://localhost:{port}  [{desc}]")
    print("Refresh the browser page to pick up new results.")
    print("Ctrl-C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")

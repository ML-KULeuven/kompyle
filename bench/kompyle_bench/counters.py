# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Count-only backend registry.

The `kompyle_bench.backends` registry covers backends that
*construct a circuit* alongside doing their model-counting work.
The registry here *only* counts, with no circuit overhead.
Pairing the two lets us measure circuit-construction
overhead per backend (``compile_time - count_time``).
"""

from __future__ import annotations

import os
import re
import shutil
import signal
import subprocess
import tempfile

from dataclasses import dataclass
from typing import Callable, Optional

import kompyle as p


@dataclass(frozen=True)
class CountOutput:
    """Result of a single count run.

    ``model_count`` is a Python ``int`` (arbitrary precision).
    """
    model_count: Optional[int]


CounterFn = Callable[..., CountOutput]

# -----------------------------------------------------------------
# sdd
# -----------------------------------------------------------------

def _sdd_count(cnf_path: str, *, cache_mb: Optional[int]) -> CountOutput:
    # SDD has no equivalent cache_mb option, we keep the parameter for
    # interface uniformity but it's a no-op on this backend.
    del cache_mb
    count = p.count_from_cnf_using_sdd(cnf_file=cnf_path)
    return CountOutput(model_count=int(count))

# -----------------------------------------------------------------
# ganak
# -----------------------------------------------------------------

def _ganak_count(cnf_path: str, *, cache_mb: Optional[int]) -> CountOutput:
    gopts = p.GanakOptions()
    aopts = p.ArjunOptions()
    aopts.do_arjun = False
    if cache_mb is not None:
        gopts.maximum_cache_size_mb = cache_mb

    count = p.count_from_cnf_using_ganak(
        cnf_file=cnf_path,
        ganak_options=gopts,
        arjun_options=aopts,
        weighted_counting=False,
    )
    return CountOutput(model_count=int(count))


def _ganak_arjun_count_impl(
    cnf_path: str, *, cache_mb: Optional[int], weighted_counting: bool,
) -> CountOutput:

    gopts = p.GanakOptions()
    aopts = p.ArjunOptions()
    if cache_mb is not None:
        gopts.maximum_cache_size_mb = cache_mb

    count = p.count_from_cnf_using_ganak(
        cnf_file=cnf_path,
        ganak_options=gopts,
        arjun_options=aopts,
        weighted_counting=weighted_counting,
    )
    return CountOutput(model_count=int(count))


def _ganak_arjun_count(cnf_path: str, *, cache_mb: Optional[int]) -> CountOutput:
    return _ganak_arjun_count_impl(
        cnf_path, cache_mb=cache_mb, weighted_counting=False,
    )


def _ganak_arjun_wmc_count(cnf_path: str, *, cache_mb: Optional[int]) -> CountOutput:
    return _ganak_arjun_count_impl(
        cnf_path, cache_mb=cache_mb, weighted_counting=True,
    )


# -----------------------------------------------------------------
# d4v2
# -----------------------------------------------------------------


def _d4v2_count(cnf_path: str, *, cache_mb: Optional[int]) -> CountOutput:
    opts = p.D4Options()
    if cache_mb is not None:
        opts.cache_first_page = cache_mb * 1024 * 1024
        # FIXME(Ibrahim): infinite-loop, doesn't crash cleanly
        # opts.cache_extra_page = 0

    count = p.count_from_cnf_using_d4v2(cnf_file=cnf_path, options=opts)
    return CountOutput(model_count=int(count))
 


# -----------------------------------------------------------------
# External-binary counters
# -----------------------------------------------------------------

_PR_SET_PDEATHSIG = 1  # from <linux/prctl.h>


def _set_pdeathsig() -> None:
    """preexec_fn: ask the kernel to SIGKILL me when my parent dies."""
    try:
        import ctypes
        libc = ctypes.CDLL("libc.so.6", use_errno=True)
        libc.prctl(_PR_SET_PDEATHSIG, signal.SIGKILL, 0, 0, 0)
    except Exception:
        # Non-Linux / no libc / older kernel. Worst case: an orphan
        # subprocess after a timeout. Not blocking for the next step.
        pass


def _resolve_binary(name: str, env_var: str) -> str:
    """Resolve a solver binary path.

    Checks ``$env_var`` first (must point to an existing file), then
    ``shutil.which(name)``. Raises FileNotFoundError with actionable
    guidance when neither finds a binary.
    """
    override = os.environ.get(env_var)
    if override:
        if not os.path.isfile(override):
            raise FileNotFoundError(
                f"{env_var} points to a non-file path: {override!r}"
            )
        return override
    found = shutil.which(name)
    if found:
        return found
    raise FileNotFoundError(
        f"{name} binary not found. Either set {env_var} to its absolute "
        f"path, or put the binary on $PATH."
    )


# MCC competition output: `c s exact arb int <N>` (ganak, d4v2).
# Older format `s mc <N>` is accepted as a fallback.
_MCC_EXACT_INT_RE = re.compile(
    r"^c\s+s\s+exact\s+arb\s+int\s+(\S+)\s*$", re.MULTILINE,
)
_MCC_S_MC_RE = re.compile(
    r"^s\s+mc\s+(\S+)\s*$", re.MULTILINE,
)
_MCC_S_BARE_RE = re.compile(
    r"^s\s+(\d+)\s*$", re.MULTILINE,
)


def _parse_mcc_count(stdout: str) -> Optional[int]:
    """Extract the model count from an MCC-format solver's stdout.

    Returns the count as a Python int, or None on parse failure. Empty
    counts (UNSAT) typically come through as 0 on the same line.
    """
    for rx in (_MCC_EXACT_INT_RE, _MCC_S_MC_RE, _MCC_S_BARE_RE):
        m = rx.search(stdout)
        if m is None:
            continue
        s = m.group(1)
        try:
            return int(s)
        except ValueError:
            try:
                # Scientific notation -> Decimal -> int. Lossy in principle
                # but the standard counters all print exact integers when
                # they print "exact arb int".
                from decimal import Decimal
                return int(Decimal(s))
            except Exception:
                return None
    return None


def _run_binary_counter(
    *,
    binary: str,
    args:   list[str],
    cnf_path: str,
    parser: Callable[[str], Optional[int]],
    name:   str,
) -> CountOutput:
    """Shared subprocess driver for every external-binary counter.

    All counters share the same exec/contain/parse machinery; only the
    argv and the output parser differ.
    """
    cnf_path = os.path.abspath(cnf_path)
    cmd = [binary, *args, cnf_path]
    with tempfile.TemporaryDirectory(prefix=f"{name}_") as tmp:
        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # interleave, parser sees everything
                cwd=tmp,                   # contain any side-effect files
                preexec_fn=_set_pdeathsig, # kill-on-parent-death (Linux)
                text=True,
                check=False,
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"failed to exec {name} at {binary!r}: {e}"
            ) from e

    if proc.returncode != 0:
        raise RuntimeError(
            f"{name} exited with code {proc.returncode}; "
            f"tail of output: {proc.stdout[-500:]!r}"
        )

    count = parser(proc.stdout)
    if count is None:
        raise RuntimeError(
            f"{name} ran successfully but no model count was found in its "
            f"output. Tail: {proc.stdout[-500:]!r}"
        )
    return CountOutput(model_count=count)


# -----------------------------------------------------------------
# isymganak (binary)
# -----------------------------------------------------------------

_SOLUTIONS_HEADER_RE = re.compile(r"^\s*#\s*solutions\b.*$", re.MULTILINE)


def _parse_isymganak_output(stdout: str) -> Optional[int]:
    """Extract the model count from isymganakker's stdout.

    Output structure on success::

        ...
        # solutions
        <decimal digits>

        # END
        ...

    Edge case: when the CNF is detected UNSAT during *file parsing* and
    the run uses ``-q``, isymganakker prints "FOUND UNSAT DURING FILE
    PARSING" but skips PrintShort, so the ``# solutions`` block is
    missing. We detect that string and return 0.
    """
    if "FOUND UNSAT DURING FILE PARSING" in stdout:
        return 0

    m = _SOLUTIONS_HEADER_RE.search(stdout)
    if m is None:
        return None

    for line in stdout[m.end():].splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            # Hit "# END" or another comment before the count, malformed.
            return None
        try:
            return int(line)
        except ValueError:
            return None
    return None


def _isymganak_bin_count(cnf_path: str, *, cache_mb: Optional[int]) -> CountOutput:
    binary = _resolve_binary("isymganakker", "ISYMGANAKKER_BIN")
    args: list[str] = []

    args += ["-q"]
    args += ["-SBS", "0"]
    args += ["-DBS", "0"]
    args += ["-FG"]
    args += ["-useL2"]
    args += ["-L2prop", "17"]

    if cache_mb is not None:
        # isymganakker's -cs is in MB
        args += ["-cs", str(int(cache_mb))]

    return _run_binary_counter(
        binary=binary, args=args, cnf_path=cnf_path,
        parser=_parse_isymganak_output, name="isymganakker",
    )


# -----------------------------------------------------------------
# ganak (binary)
# -----------------------------------------------------------------


def _ganak_bin_count(cnf_path: str, *, cache_mb: Optional[int]) -> CountOutput:
    binary = _resolve_binary("ganak", "GANAK_BIN")
    args: list[str] = []
    args += ["--arjun", "0"]
    if cache_mb is not None:
        # ganak takes --maxcache in MB.
        args += ["--maxcache", str(int(cache_mb))]
    return _run_binary_counter(
        binary=binary, args=args, cnf_path=cnf_path,
        parser=_parse_mcc_count, name="ganak",
    )

def _ganak_arjun_bin_count(cnf_path: str, *, cache_mb: Optional[int]) -> CountOutput:
    binary = _resolve_binary("ganak", "GANAK_BIN")
    args: list[str] = []
    args += ["--arjun", "1"]
    if cache_mb is not None:
        # ganak takes --maxcache in MB.
        args += ["--maxcache", str(int(cache_mb))]
    return _run_binary_counter(
        binary=binary, args=args, cnf_path=cnf_path,
        parser=_parse_mcc_count, name="ganak",
    )



# -----------------------------------------------------------------
# d4v2 (binary)
# -----------------------------------------------------------------


def _d4v2_bin_count(cnf_path: str, *, cache_mb: Optional[int]) -> CountOutput:
    binary = _resolve_binary("d4", "D4_BIN")
    args = ["-i", os.path.abspath(cnf_path)]
    cmd = [binary, *args]
    with tempfile.TemporaryDirectory(prefix="d4_") as tmp:
        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=tmp,
                preexec_fn=_set_pdeathsig,
                text=True,
                check=False,
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"failed to exec d4 at {binary!r}: {e}"
            ) from e

    if proc.returncode != 0:
        raise RuntimeError(
            f"d4 exited with code {proc.returncode}; "
            f"tail of output: {proc.stdout[-500:]!r}"
        )
    count = _parse_mcc_count(proc.stdout)
    if count is None:
        raise RuntimeError(
            f"d4 ran successfully but no model count was found in its "
            f"output. Tail: {proc.stdout[-500:]!r}"
        )
    # cache_mb is accepted for signature compatibility but not used here
    # (see comment above). The library counter `_d4v2_count` honours it.
    _ = cache_mb
    return CountOutput(model_count=count)


# -----------------------------------------------------------------
# registry
# -----------------------------------------------------------------

COUNTERS: dict[str, CounterFn] = {
    "ganak_count":              _ganak_count,
    "ganak_arjun_count":        _ganak_arjun_count,
    "ganak_arjun_wmc_count":    _ganak_arjun_wmc_count,
    "d4v2_count":               _d4v2_count,
    "sdd_count":                _sdd_count,
    # binary
    "ganak_bin_count":          _ganak_bin_count,
    "ganak_arjun_bin_count":    _ganak_arjun_bin_count,
    "d4v2_bin_count":           _d4v2_bin_count,
    "isymganak_bin_count":      _isymganak_bin_count,
}


def count_with(
    backend: str,
    cnf_path: str,
    cache_mb: Optional[int] = None,
) -> CountOutput:
    """Dispatch to the named counter. Raises :class:`ValueError` on unknown name."""
    if backend not in COUNTERS:
        raise ValueError(
            f"Unknown count-only backend {backend!r}. "
            f"Known: {sorted(COUNTERS)}."
        )
    return COUNTERS[backend](cnf_path, cache_mb=cache_mb)

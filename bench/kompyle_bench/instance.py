# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Instance abstraction.

The rest of the codebase reads exactly one set of paths,
takes exactly one set of runner functions and asks the
instance for its identity / disk location.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


class Instance(ABC):
    """A single benchmark input."""

    @property
    @abstractmethod
    def key(self) -> str:
        """Stable identifier used as the result-JSON filename stem."""

    @property
    @abstractmethod
    def label(self) -> str:
        """Short human-readable label for log lines."""

    @abstractmethod
    def cnf_path(self) -> Path:
        """Return the CNF on disk, generating it on first call if needed."""

    def read_nb_vars(self) -> int:
        """Read the variable count from the DIMACS header."""
        with self.cnf_path().open() as f:
            for line in f:
                if line.startswith("p cnf"):
                    return int(line.split()[2])
        raise ValueError(f"No 'p cnf' header in {self.cnf_path()}")


@dataclass(frozen=True)
class SyntheticInstance(Instance):
    nb_vars: int
    ratio: float
    seed: int
    instances_dir: Path = Path("instances")

    @property
    def key(self) -> str:
        return f"v{self.nb_vars}_r{self.ratio:.1f}_s{self.seed}"

    @property
    def label(self) -> str:
        return f"v={self.nb_vars:3d}  r={self.ratio:.1f}  s={self.seed}"

    def cnf_path(self) -> Path:
        path = self.instances_dir / f"{self.key}.cnf"
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            self._generate_dimacs(path, clause_count=round(self.nb_vars * self.ratio))
        return path

    def _generate_dimacs(
        self,
        path: Path,
        clause_count: int,
        clause_length: int = 3,
    ) -> None:
        rng = random.Random(self.seed)
        with path.open("w") as f:
            f.write(f"p cnf {self.nb_vars} {clause_count}\n")
            for _ in range(clause_count):
                clause = [
                    rng.randint(1, self.nb_vars) * rng.choice([1, -1])
                    for _ in range(clause_length)
                ]
                f.write(" ".join(map(str, clause)) + " 0\n")


@dataclass(frozen=True)
class RealInstance(Instance):
    path: Path

    @property
    def key(self) -> str:
        return self.path.stem

    @property
    def label(self) -> str:
        return f"cnf={self.path.name}"

    def cnf_path(self) -> Path:
        if not self.path.exists():
            raise FileNotFoundError(f"CNF file does not exist: {self.path}")
        return self.path

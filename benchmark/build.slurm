#!/bin/bash -l
#SBATCH --clusters=wice
#SBATCH --account=lp_dtai1
#SBATCH --job-name=kc_build

#SBATCH --mail-user=ibrahim.elkaddouri@student.kuleuven.be
#SBATCH --mail-type=NONE

#SBATCH --output=logs/build_%j.out
#SBATCH --error=logs/build_%j.err

#SBATCH --time=0-00:30:00

#SBATCH --partition=batch
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G

# ---------------------------------------------------------------------------
set -euo pipefail
mkdir -p logs

REPO="${VSC_DATA}/kompyle"
VENV="${VSC_SCRATCH}/venv"

module load Boost/1.85.0-GCC-13.3.0
module load CMake/3.29.3-GCCcore-13.3.0
module load SQLite/3.45.3-GCCcore-13.3.0
module load GMP/6.3.0-GCCcore-13.3.0
module load MPFR/4.2.1-GCCcore-13.3.0  2>/dev/null || true
module load zlib/1.3.1-GCCcore-13.3.0  2>/dev/null || true
module load Python
module load SciPy-bundle

export PREFIX="${VSC_SCRATCH}/install"
export SUDO=""
export BUILD_TYPE="Release"

DEPS="${REPO}/scripts/deps"
source "${DEPS}/common.sh"

for script in \
    03_flint 04_cereal 05_armadillo 06_ensmallen 07_mlpack \
    08_cadical 09_cadiback 10_breakid 11_cryptominisat 12_sbva \
    13_arjun 14_approxmc 15_ganak 17_d4v2
do
    echo "--- ${script} ---"
    bash "${DEPS}/${script}.sh"
done

# ---------------------------------------------------------------------------
[ ! -d "${VENV}" ] && python3 -m venv "${VENV}"
source "${VENV}/bin/activate"
pip install --upgrade pip wheel scikit-build-core "nanobind>=1.3.2"
pip install "klaycircuits @ git+https://github.com/IbrahimElk/klay.git@tmp"
pip install --no-build-isolation \
    -Ccmake.define.CMAKE_PREFIX_PATH="${PREFIX}" \
    "${REPO}"
pip install pysdd numpy pandas matplotlib tqdm

echo "=== build complete ==="

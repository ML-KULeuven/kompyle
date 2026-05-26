# Sweep scripts

Everything that orchestrates running the benchmark across a sweep grid.

## Quickstart

### On your workstation

```sh
# run the full synthetic sweep (compile + count + infer + experiment) on local cores
bash scripts/local/sweep_synth.sh 7              # exp_id = 7

# just the count phase
bash scripts/local/sweep_synth.sh 7 count

# real instances, only the compile phase
bash scripts/local/sweep_real.sh 8 compile

# pass through extra options to GNU parallel after `--`
bash scripts/local/sweep_synth.sh 7 all -- --jobs 8
```

### On the HPC

```sh
source scripts/slurm/sbatch_defaults.sh          # cluster / account / mail

sbatch scripts/slurm/build.slurm                 # one-shot venv, ~5 min

# compile (default stage)
bash scripts/slurm/submit_synth.sh 7              # 1056 tasks, 32G/task, auto-chunked
bash scripts/slurm/submit_real.sh  8 compile 64   # real, 64G/task

# count
bash scripts/slurm/submit_synth.sh 7 count 8      # synth count array, 8G/task
bash scripts/slurm/submit_real.sh  8 count 16     # real count array, 16G/task
```

`build.slurm` creates a venv and runs `pip install kompyle==<version>`,
pulling a published binary wheel. The pinned version lives in `build.slurm` itself,
override with `KOMPYLE_VERSION=...` when sbatch'ing.

## Editing the sweep grid

There is **one** file, `lib/grid.sh`. Local and SLURM both source it.
If you need a different grid for a one-off run, override on the command
line. Every array variable can be set in the environment before
sourcing, but it's cleaner to commit a new `grid_*.sh` and update the
`source` line.

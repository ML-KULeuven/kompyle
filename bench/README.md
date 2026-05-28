# benchmark/

Sweep, time and visualise compile + inference performance across knowledge-compilation backends.

## Stages

| stage | what it does | output |
|---|---|---|
| `compile`    | Compile the CNF into a klay circuit. Reports compile time + circuit size. | `results/compile/<backend>/<key>.json` |
| `count`      | Model-count the CNF *without* building a circuit. Pairs with `compile` to measure circuit-construction overhead. | `results/count/<backend>/<key>.json` |
| `infer`      | Time forward / backward passes through the compiled circuit. | `results/infer/<backend>_<semiring>_<device>/<key>.json` |
| `experiment` | Structural analysis of the compiled circuit (relay layers, dummy edges). | `results/experiment/dummy_overhead/<backend>_<semiring>_<device>/<key>.json` |

## Results

The web folder, which provides a web server for an interactive map of the results, was mostly written using AI.
The bash scripts, originally from the ISYMGANAK codebase, were adapted using AI.
The Python benchmarking code also comes from the Klay codebase but has been extended for our use case.

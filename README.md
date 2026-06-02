# Kompyle

Kompyle is a Python library providing an interface to several d-DNNF knowledge compilers.

---

## Installation

Kompyle can be installed using the following command:

    pip install kompyle

## Examples

A Jupyter notebook with usage examples is included in `scripts/` folder.
It demonstrates how to use Kompyle for compiling.

## License

Kompyle itself is licensed under the **Apache License 2.0** — see [LICENSE](LICENSE).

### Important notice regarding bundled libraries

This binary wheel bundles several third-party libraries. Two carry restrictions
beyond the Apache 2.0 license that users should be aware of:

- **PaToH** (compiled into `libmd4`) is licensed for **non-commercial and academic /
  research use only**. Commercial use requires a paid license from
  Ümit V. Çatalyürek (umit@gatech.edu). See
  [licenses/LICENSE-PaToH.txt](licenses/LICENSE-PaToH.txt) for details.

- **bipe** (compiled into `libmd4`) is licensed under the **AGPL-3.0**. The
  corresponding source is available at <https://github.com/crillab/d4v2>.

Full license texts and attribution notices for all bundled libraries are in the
[licenses/](licenses/) directory.

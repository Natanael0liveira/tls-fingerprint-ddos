# Submission metadata

[NOMS 2027](noms2027/README.md) records submitted-source hashes, historical PDF
validation and the scope of checks on the public artifact. Complete TeX/PDF
manuscripts and upload projects are not distributed in the current tree.

The authors keep a separate local freeze under `archive/local/`, ignored by Git.
Public artifact checks run with `make check`; `make artifact` refreshes only the
public checksum manifest. Earlier Git history still contains manuscript files.

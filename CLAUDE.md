# Project notes

## Known Bugs

The original Rust 1.99.1 constant-chunk diagnostics have been repaired with
fixed-array iteration. The selected scalar/default x64 and AArch64 strict
Clippy configurations pass. Other CI configurations retain their own verdicts. See [CMYK float conversion](docs/CMYK_FLOAT_CONVERSION.md)
for the tested source, selected coverage and remaining numerical scope.

The inherited external mirror workflow is restricted to its originating
repository. Fork pushes must not attempt to publish to those destinations.

Rust 1.100 Clippy also checks the final matrix-equality predicate. Its
negated comparison keeps the original tolerance, row evaluation and NaN
behavior. The complete scalar library tests pass with that compiler. The
first attempted `matrix::` filter selected no tests and supplies no runtime
evidence.


Rust 1.100 also flags the LUT linearity boolean tail in `trc.rs`. The
expression now returns `is_curve_linear16(lut)` directly, preserving the
earlier empty-LUT and curve branches. Strict scalar Clippy and all scalar
library tests pass with Rust 1.100. CPU-emulation CI remains under a
separate instruction-trace investigation.


The inherited SSE/AVX2-isolated jobs still report SIGILL. Local Nehalem
controls pass for a trivial Rust test, the unchanged baseline and the
candidate, including CI's exact nightly 1.102.0 (59cbdee2e). This does not
explain the remote failure. The CI jobs now retain a startup instruction
trace and minimal-process control before the unchanged full test loops.
The diagnostic records child status; it does not replace a test verdict.

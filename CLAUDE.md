# Project notes

## Known Bugs

The original Rust 1.99.1 constant-chunk diagnostics have been repaired with
fixed-array iteration. The selected scalar/default x64 and AArch64 strict
Clippy configurations pass. Other CI configurations retain their own verdicts. See [CMYK float conversion](docs/CMYK_FLOAT_CONVERSION.md)
for the tested source, selected coverage and remaining numerical scope.

The inherited external mirror workflow is restricted to its originating
repository. Fork pushes must not attempt to publish to those destinations.

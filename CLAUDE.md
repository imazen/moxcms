# Project notes

## Known Bugs

Strict Clippy on Rust 1.99.1 retains constant-chunk diagnostics in the existing
library and tests. The CMYK repair introduces no additional warning in the
baseline/candidate census. See [CMYK float conversion](docs/CMYK_FLOAT_CONVERSION.md)
for the tested source, selected coverage and remaining numerical scope.

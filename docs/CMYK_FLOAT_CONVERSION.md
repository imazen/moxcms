# Direct CMYK float conversion

With `any_to_any`, a LUT whose curves require separate evaluation uses the
original tables rather than the fused grid. Float output on this path now
honors `allow_extended_range_rgb_xyz` when the destination has an analytic
common transfer curve. The matrix and curve evaluator is shared with the
existing extended-range path. The final copy validates source and destination
lane lengths before writing caller output.

For direct four-input LUTs, an explicit float `Tetrahedral` request interpolates
the first input between two three-dimensional tetrahedra over the remaining
inputs. This matches the axis convention of
[LCMS Eval4InputsFloat](https://github.com/mm2/Little-CMS/blob/lcms2.17/src/cmsintrp.c).
Default linear interpolation and integer dispatch retain their existing paths.
This change applies to direct `LutDataType` input; it does not qualify every
multidimensional profile, curve, rendering intent or CMS against LCMS.

The alpha finalizer now requires both an RGB/gray profile model and a matching
alpha layout before copying alpha. A four-ink CMYK buffer using `Layout::Rgba`
has no alpha; RGB output with alpha receives an opaque sample.

## Evidence and limits

The regression constructs the original LUT and destination matrix explicitly.
It checks a source knot, an independently computed tetrahedron weight, negative
and above-one output, F32/F64, RGB/RGBA storage, opaque alpha, disabled extended
range, and malformed output lanes with an unchanged destination. On the
preceding default-branch source, the extended test returns 1 instead of 2 and
the tetrahedron test returns 0.0060121464 instead of 0.03. The original-knot
control passes. The alpha test separately exposed K copied as alpha.

`just cmyk-float-check` runs the focused and library checks plus feature builds.
The functional checks and feature builds pass locally with Rust 1.99.1.
Strict Clippy is not green: the library has 44 existing constant-chunk lints.
A separate library-and-tests warning census reports 96 diagnostics on both
baseline and candidate, with no new diagnostic after normalizing source spans.
No lint allowance or existing expectation was changed.

`just cmyk-float-coverage <new-directory>` retains LLVM JSON;
`just cmyk-float-region-report <json> <output>` reports selected regions. The
observed selection is 20/20 alpha regions, 36/37 extended-output regions,
48/51 tetrahedral-selection regions and 15/15 extended-selection regions.
The extended evaluator always returns success, leaving its error-propagation
region unexecuted. The tetrahedral gaps are a zero-grid refusal and two
allocation-free cube-validation propagation regions after the complete
hypercube has already been validated. These fractions merge generic
instantiations and do not establish complete boolean or platform coverage.

The encoder investigation also compared the Artifex PS CMYK profile's 251-step
Black gradient with independent LCMS 2.17 output. Maximum linear-RGB difference
changed from 0.00302953017 to 0.00029194355 with the selected direct tetrahedral
float path. This is one profile and one gradient, not universal CMS parity.
Allocator-failure injection, broad profile qualification and cross-platform
numerical qualification remain separate work.

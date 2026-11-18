# Changelog

## [Unreleased]

### QUEUED BREAKING CHANGES

None.

### Fixed

- Direct float LUT output preserves requested extended RGB range when an
  analytic destination curve is available.
- Direct four-input float LUTs consume an explicit tetrahedral interpolation
  request using the first input as the slab axis.
- Alpha finalization checks the profile channel model together with storage
  layout, preserving CMYK's fourth ink as ink.

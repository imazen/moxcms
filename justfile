# Pure Rust original-LUT controls; the test explicitly selects both required features.
cmyk-float-knot:
    cargo test -p moxcms --no-default-features --features any_to_any,extended_range,options --test cmyk_float_lut

cmyk-float-check:
    cargo fmt -p moxcms
    just cmyk-float-knot
    cargo test -p moxcms --lib --no-default-features --features any_to_any,extended_range,options
    cargo check -p moxcms --no-default-features --features any_to_any
    cargo check -p moxcms --no-default-features --features any_to_any,options
    cargo check -p moxcms --no-default-features --features extended_range
    cargo clippy -p moxcms --no-default-features --features any_to_any,extended_range,options --lib --test cmyk_float_lut -- -D warnings

cmyk-float-lint-census manifest output:
    cargo clippy --manifest-path {{quote(manifest)}} -p moxcms --no-default-features --features any_to_any,extended_range,options --lib --tests --message-format=json > {{quote(output)}}

cmyk-float-coverage output:
    mkdir {{quote(output)}}
    cargo llvm-cov test -p moxcms --no-default-features --features any_to_any,extended_range,options --test cmyk_float_lut --no-report
    cargo llvm-cov test -p moxcms --no-default-features --features any_to_any,extended_range,options --lib alpha_finalizer_tests --no-report
    cargo llvm-cov report --json --output-path {{quote(output + "/coverage.json")}}

cmyk-float-region-report coverage output:
    python3 tools/cmyk_region_report.py {{quote(coverage)}} {{quote(output)}}

cmyk-float-lint-fix:
    cargo clippy --fix --allow-dirty -p moxcms --no-default-features --features any_to_any,extended_range,options --lib --tests -- -D warnings

cmyk-lint-final:
    cargo clippy -p moxcms --no-default-features --features any_to_any,extended_range,options --lib --tests -- -D warnings
    cargo clippy -p moxcms --features any_to_any,extended_range,options,in_place --lib --tests -- -D warnings
    cargo test -p moxcms --features any_to_any,extended_range,options,in_place --lib --test cmyk_float_lut

cmyk-lint-arm:
    cargo clippy -p moxcms --target aarch64-unknown-linux-gnu --features any_to_any,extended_range,options,in_place --lib --tests -- -D warnings

cmyk-array-identity base output:
    python3 tools/check_array_iteration.py {{quote(base)}} {{quote(output)}}

matrix-current-lint:
    cargo +1.100.0 clippy -p moxcms --no-default-features --lib -- -D warnings
    cargo +1.100.0 test -p moxcms --no-default-features --lib

// Copyright (c) Imazen LLC. Licensed under Apache-2.0 OR BSD-3-Clause.
#![cfg(all(
    feature = "any_to_any",
    feature = "extended_range",
    feature = "options"
))]
use moxcms::{
    ColorProfile, DataColorSpace, Layout, LutDataType, LutStore, LutType, LutWarehouse, Matrix3d,
    RenderingIntent, TransformOptions, Xyzd,
};

fn profiles() -> (ColorProfile, ColorProfile) {
    let mut source = ColorProfile::new_srgb();
    source.color_space = DataColorSpace::Cmyk;
    source.cicp = None;
    // Four source grid points do not coincide with the fused 17-point grid.
    // Only K varies. At K=1/3 the original table's exact output is 8192/32768.
    let mut table = Vec::new();
    for _c in 0..4 {
        for _m in 0..4 {
            for _y in 0..4 {
                for k in [0, 8192, 10000, 16384] {
                    table.extend_from_slice(&[k, k, k]);
                }
            }
        }
    }
    source.lut_a_to_b_perceptual = Some(LutWarehouse::Lut(LutDataType {
        num_input_channels: 4,
        num_output_channels: 3,
        num_clut_grid_points: 4,
        matrix: Matrix3d {
            v: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]],
        },
        num_input_table_entries: 2,
        num_output_table_entries: 2,
        input_table: LutStore::Store16([0, 65535].repeat(4)),
        output_table: LutStore::Store16([0, 65535].repeat(3)),
        clut_table: LutStore::Store16(table),
        lut_type: LutType::Lut16,
    }));
    let mut target = ColorProfile::new_srgb();
    target.red_colorant = Xyzd::new(1., 0., 0.);
    target.green_colorant = Xyzd::new(0., 1., 0.);
    target.blue_colorant = Xyzd::new(0., 0., 1.);
    let curve = moxcms::curve_from_gamma(1.);
    target.red_trc = Some(curve.clone());
    target.green_trc = Some(curve.clone());
    target.blue_trc = Some(curve);
    target.cicp = None;
    (source, target)
}
fn options() -> TransformOptions {
    TransformOptions {
        rendering_intent: RenderingIntent::Perceptual,
        allow_use_cicp_transfer: false,
        allow_extended_range_rgb_xyz: true,
        prefer_fixed_point: false,
        ..Default::default()
    }
}
#[test]
fn float_cmyk_preserves_original_lut_knot() {
    let (source, target) = profiles();
    let transform = source
        .create_transform_f32(Layout::Rgba, &target, Layout::Rgb, options())
        .unwrap();
    let mut output = [f32::NAN; 3];
    transform
        .transform(&[0.17, 0.43, 0.91, 1. / 3.], &mut output)
        .unwrap();
    for value in output {
        assert!(
            (value - 0.25).abs() < 0.0001,
            "original K knot: {value} != 0.25"
        );
    }
}
#[test]
fn direct_float_cmyk_preserves_extended_rgb() {
    for (red, blue, expected) in [
        (
            Xyzd::new(0.125, 0., 0.),
            Xyzd::new(0., 0., 1.),
            [2., 0.25, 0.25],
        ),
        (
            Xyzd::new(1., 0., 0.),
            Xyzd::new(2., 0., 1.),
            [-0.25, 0.25, 0.25],
        ),
    ] {
        let (source, mut target) = profiles();
        target.red_colorant = red;
        target.blue_colorant = blue;
        let transform = source
            .create_transform_f32(Layout::Rgba, &target, Layout::Rgb, options())
            .unwrap();
        let mut output = [f32::NAN; 3];
        transform
            .transform(&[0.17, 0.43, 0.91, 1. / 3.], &mut output)
            .unwrap();
        for (actual, expected) in output.into_iter().zip(expected) {
            assert!(
                (actual - expected).abs() < 0.0001,
                "extended RGB {actual} != {expected}"
            );
        }
    }
}
#[test]
fn requested_tetrahedral_cmyk_interpolates_first_axis_between_3d_simplices() {
    let (mut source, target) = profiles();
    let LutWarehouse::Lut(lut) = source.lut_a_to_b_perceptual.as_mut().unwrap() else {
        unreachable!()
    };
    lut.num_clut_grid_points = 2;
    let mut table = vec![0; 2_usize.pow(4) * 3];
    table[15 * 3..].fill(16384);
    lut.clut_table = LutStore::Store16(table);
    let mut options = options();
    options.interpolation_method = moxcms::InterpolationMethod::Tetrahedral;
    let transform = source
        .create_transform_f32(Layout::Rgba, &target, Layout::Rgb, options)
        .unwrap();
    let mut output = [f32::NAN; 3];
    transform
        .transform(&[0.2, 0.3, 0.4, 0.5], &mut output)
        .unwrap();
    // C selects between two slabs. On the upper slab, the sole nonzero
    // tetrahedron vertex has weight min(M,Y,K)=0.3. XYZ normalization is 0.5.
    for value in output {
        assert!(
            (value - 0.03).abs() < 0.0001,
            "tetrahedral K interaction: {value} != 0.03"
        );
    }
}
#[test]
fn direct_f64_cmyk_preserves_extended_rgba_and_opaque_alpha() {
    let (source, mut target) = profiles();
    target.red_colorant = Xyzd::new(0.125, 0., 0.);
    let transform = source
        .create_transform_f64(Layout::Rgba, &target, Layout::Rgba, options())
        .unwrap();
    let mut output = [f64::NAN; 4];
    transform
        .transform(&[0.17, 0.43, 0.91, 1. / 3.], &mut output)
        .unwrap();
    for (actual, expected) in output.into_iter().zip([2., 0.25, 0.25, 1.]) {
        assert!(
            (actual - expected).abs() < 0.0001,
            "extended RGBA {actual} != {expected}"
        );
    }
}
#[test]
fn unrequested_extended_range_keeps_clipped_output() {
    let (source, mut target) = profiles();
    target.red_colorant = Xyzd::new(0.125, 0., 0.);
    let mut options = options();
    options.allow_extended_range_rgb_xyz = false;
    let transform = source
        .create_transform_f32(Layout::Rgba, &target, Layout::Rgb, options)
        .unwrap();
    let mut output = [f32::NAN; 3];
    transform
        .transform(&[0.17, 0.43, 0.91, 1. / 3.], &mut output)
        .unwrap();
    assert_eq!(output[0], 1.0);
}
#[test]
fn extended_output_rejects_malformed_lanes_without_writing_destination() {
    let (source, target) = profiles();
    let transform = source
        .create_transform_f32(Layout::Rgba, &target, Layout::Rgb, options())
        .unwrap();
    for length in [2, 6] {
        let mut output = vec![123.0; length];
        assert!(
            transform
                .transform(&[0.17, 0.43, 0.91, 1. / 3.], &mut output)
                .is_err()
        );
        assert!(output.iter().all(|&value| value == 123.0));
    }
}

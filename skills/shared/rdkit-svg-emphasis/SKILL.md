---
name: rdkit-svg-emphasis
description: "Create publication-style RDKit SVG molecular figures with reusable visual emphasis: fully filled atom-and-bond region envelopes, dashed outer contours, transparent backgrounds, native RDKit typography, and optional stereo annotations. Use when a user asks to highlight, group, compare, classify, or visually encode arbitrary molecular atom sets in SVG; subgraphs and substituents are only example semantics, not fixed meanings."
---

# RDKit SVG Emphasis

Treat emphasis as a visual encoding over arbitrary atom sets. Let the caller decide whether a set means a subgraph, substituent, pharmacophore, reaction center, uncertainty region, model attribution, matched scaffold, or another concept.

## Workflow

1. Parse and sanitize the molecule with RDKit.
2. Assign stereochemistry before drawing.
3. Define non-overlapping or intentionally overlapping atom sets.
4. Choose one of two emphasis primitives per set:
   - `filled_regions`: a complete colored envelope behind the molecule.
   - `outline_regions`: one dashed outer contour with no internal ring contour.
5. Render the molecule with RDKit first so `GetDrawCoords()` uses final coordinates.
6. Generate emphasis SVG paths from those coordinates.
7. Insert emphasis immediately after `<!-- END OF HEADER -->`; this places it behind RDKit bonds and labels.
8. Parse the resulting XML and visually inspect a raster preview.

Use `scripts/render_emphasis.py` instead of rewriting the SVG geometry.

```bash
python scripts/render_emphasis.py \
  --smiles 'CCO' \
  --config emphasis.json \
  --output molecule.svg
```

The config contains the semantics only as names; geometry is driven by atom indices:

```json
{
  "filled_regions": [
    {"name": "region A", "atoms": [0, 1], "color": "#F7E6A1", "padding": 24, "opacity": 0.72}
  ],
  "outline_regions": [
    {"name": "feature B", "atoms": [1, 2], "color": "#2F6DAE", "padding": 18, "stroke_width": 3.0, "dash": [10, 7]}
  ]
}
```

## How the SVG elements are built

### Atom-and-bond skeleton

For each atom set:

- Convert every atom draw coordinate into a Shapely `Point`.
- Convert every internal bond whose two endpoints are in the set into a `LineString`.
- Merge all points and lines with `unary_union`.
- Apply a round `buffer(padding)` to form a continuous molecular envelope.

This follows molecular topology more closely than a rectangle or convex hull.

### Filled region

For each buffered polygon, rebuild `Polygon(polygon.exterior)` before serialization. This deliberately removes internal holes, including benzene-ring centers, so the covered area is fully colored. Emit:

```svg
<path d="..." fill="#F7E6A1" fill-opacity="0.72" stroke="none"/>
```

Use a larger `padding` than the dashed contour when the fill should sit outside it.

### Dashed outer contour

Serialize only `polygon.exterior`; never serialize polygon interiors. This produces one outer contour around a ring or branched group instead of inner and outer dashed rings. Emit:

```svg
<path d="..." fill="none" stroke="#2F6DAE" stroke-width="3"
      stroke-dasharray="10 7" stroke-linecap="round" stroke-linejoin="round"/>
```

Keep dash length, gap, and stroke width proportional to final physical output size.

### Layer order

Use this order:

1. filled regions;
2. dashed outlines;
3. RDKit molecule paths and labels.

Do not append emphasis after the molecule: opaque fills would cover chemical bonds and atom labels.

## Drawing constraints

- Keep `clearBackground=False` for transparent SVG output.
- Set fonts through `MolDrawOptions.fontFile`; do not rewrite `font-family` strings after rendering.
- Prefer `addStereoAnnotation=True` for native RDKit E/Z and CIP display.
- Keep chemical semantics separate from visual semantics. Colors and contours must never change atom, bond, charge, or stereo data.
- Validate every atom index against `mol.GetNumAtoms()` and reject invalid or empty regions.
- Use explicit physical scaling when claiming journal compliance. Pixel values alone are not publication standards.
- Preserve SVG editability and avoid rasterizing until a PNG preview or delivery copy is requested.

## Validation

Run all of the following:

1. Parse the SVG with `xml.etree.ElementTree`.
2. Confirm the number of filled and outlined paths matches the region configuration, allowing multiple polygons only for disconnected atom sets.
3. Confirm a transparent background by checking that no full-canvas background rectangle was emitted.
4. Rasterize at delivery resolution and inspect boundaries, label legibility, fill overlap, and alpha corners.
5. Re-parse the original molecule and verify stereochemistry independently; emphasis generation must not mutate it.

## Generalization examples

- Fill a conserved scaffold and outline variable R groups.
- Fill model-attributed atoms and outline an experimental reaction center.
- Use different outline colors for matched, uncertain, and rejected fragments.
- Fill two compared pharmacophores with overlapping translucent envelopes.
- Outline atoms selected by a SMARTS match without calling them substituents.

Always describe the visual meaning chosen for the current figure. Do not hard-code “fill means subgraph” or “dash means substituent” into the reusable method.

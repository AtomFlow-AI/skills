---
name: rdkit-nature-style
description: "Render molecules with RDKit in a measured, monochrome Nature-like publication style using fixed physical bond length, line width, Arial typography, balanced atom-label clearance, SVG or PNG output, and mandatory post-render measurements. Use when a user asks for Nature-style, journal-style, publication-ready, or physically calibrated RDKit structure drawings without molecular-region emphasis."
---

# RDKit Nature Style

Treat "Nature style" as a local Nature-like preset, not an official RDKit or Nature preset. Preserve chemical structure and stereochemistry; change presentation only.

## Workflow

1. Confirm RDKit is available.
2. Run `scripts/render_nature_style.py` with a SMILES and output path.
3. Prefer SVG for publication and editability. Use PNG only when raster output is requested.
4. Read the generated `*.measurements.json` after every render.
5. Reject the result if the command reports a bond-length tolerance failure.
6. Visually inspect the finished structure for label collisions, excessive label clearance, clipping, and stereo legibility.

```bash
python scripts/render_nature_style.py \
  --smiles 'ClC1=CC(C=O)=C(O)C2=C1OCC2' \
  --output molecule.svg
```

## Preset

- Mean atom-center bond length: 0.381 cm.
- Bond line width: 0.021 cm.
- Multiple-bond offset: 18% of bond length.
- Font: Arial Regular when `arial.ttf` is found; otherwise RDKit's built-in font.
- Font size: 6 pt.
- Extra atom-label padding: 0.035 in RDKit relative units.
- Foreground/background: black on white.
- Atom indices: hidden.

Do not pass physical centimetres directly to `MolDrawOptions`. The script converts cm and pt at render time using `--dpi`, normalizes `fixedBondLength` by `MeanBondLength(mol)`, and then measures the final atom coordinates. RDKit's `fixedBondLength` is pixels per molecule-coordinate unit, not the final atom-to-atom length.

## Controls

```bash
python scripts/render_nature_style.py --help
```

Use the default 520 by 380 canvas for ordinary small molecules. Increase the canvas for larger molecules. Do not use `--width -1 --height -1` when physical bond length must be preserved: RDKit flexiCanvas rescales the drawing. A canvas may add whitespace or constrain the structure, but it must not define the intended bond, stroke, or font dimensions; the post-render measurement is authoritative.

Only change `--label-padding` to tune bond-to-label clearance. Do not compensate by changing bond length or font size. Use small increments such as 0.005.

## Validation

Require all of the following:

- The molecule parses and sanitizes.
- Every final atom-center bond length is measured.
- The mean bond length is within `--tolerance-cm` of the requested value.
- For SVG, actual emitted `stroke-width` values are extracted and converted back to cm.
- The configured font size is converted back to pt.
- The measurement JSON accompanies the output.
- The molecule is re-parsed from the input; drawing must not change its chemistry.

State measured values rather than claiming exact journal compliance. Nature journals may impose figure-level requirements outside a molecular renderer, including final panel dimensions, reduction, file format, and editorial typography.

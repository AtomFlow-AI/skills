#!/usr/bin/env python3
"""Render and measure a monochrome Nature-like RDKit structure drawing."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D


CM_PER_INCH = 2.54


def cm_to_px(value_cm: float, dpi: float) -> float:
    return value_cm * dpi / CM_PER_INCH


def pt_to_px(value_pt: float, dpi: float) -> float:
    return value_pt * dpi / 72.0


def apply_style(drawer, mol, args) -> None:
    opts = drawer.drawOptions()
    coordinate_bond_length = rdMolDraw2D.MeanBondLength(mol)
    if coordinate_bond_length <= 0:
        raise ValueError("Cannot determine a positive mean coordinate bond length")

    opts.fixedBondLength = cm_to_px(args.bond_length_cm, args.dpi) / coordinate_bond_length
    opts.bondLineWidth = cm_to_px(args.line_width_cm, args.dpi)
    opts.scaleBondWidth = False
    opts.multipleBondOffset = args.multiple_bond_offset
    opts.fixedFontSize = round(pt_to_px(args.font_size_pt, args.dpi))
    opts.minFontSize = opts.fixedFontSize
    opts.maxFontSize = opts.fixedFontSize
    opts.additionalAtomLabelPadding = args.label_padding
    opts.padding = args.canvas_padding
    opts.addAtomIndices = False
    opts.explicitMethyl = False
    opts.prepareMolsBeforeDrawing = True
    opts.clearBackground = True

    font = Path(args.font_file) if args.font_file else Path(r"C:\Windows\Fonts\arial.ttf")
    if font.is_file():
        opts.fontFile = str(font)
    rdMolDraw2D.SetMonochromeMode(opts, (0, 0, 0), (1, 1, 1))


def measure(drawer, mol, args, svg: str | None) -> dict:
    lengths_px = []
    for bond in mol.GetBonds():
        start = drawer.GetDrawCoords(bond.GetBeginAtomIdx())
        end = drawer.GetDrawCoords(bond.GetEndAtomIdx())
        lengths_px.append(math.hypot(end.x - start.x, end.y - start.y))
    if not lengths_px:
        raise ValueError("Measurement requires at least one bond")

    strokes_px = [] if svg is None else [
        float(value) for value in re.findall(r"stroke-width:([0-9.]+)px", svg)
    ]
    opts = drawer.drawOptions()
    mean_px = sum(lengths_px) / len(lengths_px)
    return {
        "dpi": args.dpi,
        "bond_count": len(lengths_px),
        "bond_lengths_px": [round(value, 4) for value in lengths_px],
        "bond_lengths_cm": [round(value * CM_PER_INCH / args.dpi, 6) for value in lengths_px],
        "mean_bond_length_px": round(mean_px, 4),
        "mean_bond_length_cm": round(mean_px * CM_PER_INCH / args.dpi, 6),
        "svg_stroke_widths_px": sorted(set(strokes_px)),
        "svg_stroke_widths_cm": sorted({round(value * CM_PER_INCH / args.dpi, 6) for value in strokes_px}),
        "font_size_px": opts.fixedFontSize,
        "font_size_pt": round(opts.fixedFontSize * 72 / args.dpi, 4),
        "label_padding": opts.additionalAtomLabelPadding,
    }


def render(args) -> dict:
    mol = Chem.MolFromSmiles(args.smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {args.smiles}")
    canonical_before = Chem.MolToSmiles(mol, isomericSmiles=True)
    AllChem.Compute2DCoords(mol)

    suffix = args.output.suffix.lower()
    if suffix == ".svg":
        drawer = rdMolDraw2D.MolDraw2DSVG(args.width, args.height)
    elif suffix == ".png":
        if args.width < 1 or args.height < 1:
            raise ValueError("PNG output requires positive --width and --height")
        drawer = rdMolDraw2D.MolDraw2DCairo(args.width, args.height)
    else:
        raise ValueError("Output extension must be .svg or .png")

    apply_style(drawer, mol, args)
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    data = drawer.GetDrawingText()
    report = measure(drawer, mol, args, data if suffix == ".svg" else None)
    report["canonical_smiles"] = canonical_before

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if suffix == ".svg":
        args.output.write_text(data, encoding="utf-8")
    else:
        args.output.write_bytes(data)
    args.output.with_suffix(args.output.suffix + ".measurements.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--smiles", required=True)
    result.add_argument("--output", required=True, type=Path)
    result.add_argument("--width", type=int, default=520)
    result.add_argument("--height", type=int, default=380)
    result.add_argument("--dpi", type=float, default=300.0)
    result.add_argument("--bond-length-cm", type=float, default=0.381)
    result.add_argument("--line-width-cm", type=float, default=0.021)
    result.add_argument("--font-size-pt", type=float, default=6.0)
    result.add_argument("--multiple-bond-offset", type=float, default=0.18)
    result.add_argument("--label-padding", type=float, default=0.035)
    result.add_argument("--canvas-padding", type=float, default=0.06)
    result.add_argument("--font-file")
    result.add_argument("--tolerance-cm", type=float, default=0.005)
    return result


def main() -> None:
    args = parser().parse_args()
    report = render(args)
    print(json.dumps(report, indent=2))
    error = abs(report["mean_bond_length_cm"] - args.bond_length_cm)
    if error > args.tolerance_cm:
        raise SystemExit(
            f"MEASUREMENT FAILED: mean bond length error {error:.6f} cm exceeds "
            f"tolerance {args.tolerance_cm:.6f} cm"
        )


if __name__ == "__main__":
    main()

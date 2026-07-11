#!/usr/bin/env python3
"""Render an RDKit SVG with topology-following filled and dashed emphasis regions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from rdkit import Chem
from rdkit.Chem import AllChem, Draw
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smiles", required=True)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def _path_data(polygon: Polygon) -> str:
    coords = list(polygon.exterior.coords)
    commands = [f"M {coords[0][0]:.1f},{coords[0][1]:.1f}"]
    commands.extend(f"L {x:.1f},{y:.1f}" for x, y in coords[1:])
    commands.append("Z")
    return " ".join(commands)


def _validated_atoms(region: dict[str, Any], atom_count: int) -> set[int]:
    atoms = region.get("atoms")
    if not isinstance(atoms, list) or not atoms:
        raise ValueError(f"Region {region.get('name', '<unnamed>')!r} needs atoms")
    if any(not isinstance(atom, int) or atom < 0 or atom >= atom_count for atom in atoms):
        raise ValueError(f"Invalid atom index in region {region.get('name', '<unnamed>')!r}")
    return set(atoms)


def _envelope(drawer, mol: Chem.Mol, atom_ids: set[int], padding: float):
    coords = {
        atom_id: (
            drawer.GetDrawCoords(atom_id).x,
            drawer.GetDrawCoords(atom_id).y,
        )
        for atom_id in atom_ids
    }
    skeleton = [Point(coords[atom_id]) for atom_id in atom_ids]
    skeleton.extend(
        LineString([coords[bond.GetBeginAtomIdx()], coords[bond.GetEndAtomIdx()]])
        for bond in mol.GetBonds()
        if bond.GetBeginAtomIdx() in atom_ids and bond.GetEndAtomIdx() in atom_ids
    )
    return unary_union(skeleton).buffer(float(padding), resolution=12)


def _polygons(geometry):
    return list(geometry.geoms) if hasattr(geometry, "geoms") else [geometry]


def _filled_svg(drawer, mol: Chem.Mol, regions: list[dict[str, Any]]) -> str:
    paths = ["<g id='emphasis-filled-regions'>"]
    for region in regions:
        atoms = _validated_atoms(region, mol.GetNumAtoms())
        envelope = _envelope(drawer, mol, atoms, region.get("padding", 24))
        for polygon in _polygons(envelope):
            outer = Polygon(polygon.exterior)
            paths.append(
                f"<path d='{_path_data(outer)}' fill='{region['color']}' "
                f"fill-opacity='{float(region.get('opacity', 0.72)):.3g}' stroke='none'/>"
            )
    paths.append("</g>")
    return "\n".join(paths)


def _outlined_svg(drawer, mol: Chem.Mol, regions: list[dict[str, Any]]) -> str:
    paths = ["<g id='emphasis-dashed-outlines'>"]
    for region in regions:
        atoms = _validated_atoms(region, mol.GetNumAtoms())
        envelope = _envelope(drawer, mol, atoms, region.get("padding", 18))
        dash = region.get("dash", [10, 7])
        if not isinstance(dash, list) or len(dash) != 2:
            raise ValueError("dash must contain [length, gap]")
        for polygon in _polygons(envelope):
            outer = Polygon(polygon.exterior)
            paths.append(
                f"<path d='{_path_data(outer)}' fill='none' stroke='{region['color']}' "
                f"stroke-width='{float(region.get('stroke_width', 3)):.3g}' "
                f"stroke-dasharray='{float(dash[0]):.3g} {float(dash[1]):.3g}' "
                "stroke-linecap='round' stroke-linejoin='round'/>"
            )
    paths.append("</g>")
    return "\n".join(paths)


def render(smiles: str, config: dict[str, Any]) -> str:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("Could not parse SMILES")
    Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
    AllChem.Compute2DCoords(mol)

    canvas = config.get("canvas", {})
    width = int(canvas.get("width", 1000))
    height = int(canvas.get("height", 720))
    drawer = Draw.rdMolDraw2D.MolDraw2DSVG(width, height)
    opts = drawer.drawOptions()
    opts.clearBackground = False
    opts.bondLineWidth = float(config.get("bond_line_width", 2.0))
    opts.fixedBondLength = float(config.get("fixed_bond_length", -1))
    opts.fixedFontSize = int(config.get("fixed_font_size", -1))
    opts.padding = float(config.get("drawing_padding", 0.08))
    opts.addStereoAnnotation = bool(config.get("add_stereo_annotation", True))
    font_file = config.get("font_file")
    if font_file:
        opts.fontFile = str(font_file)

    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    svg = drawer.GetDrawingText()
    emphasis = "\n".join(
        [
            _filled_svg(drawer, mol, config.get("filled_regions", [])),
            _outlined_svg(drawer, mol, config.get("outline_regions", [])),
        ]
    )
    marker = "<!-- END OF HEADER -->"
    if marker not in svg:
        raise ValueError("RDKit SVG header marker is missing")
    svg = svg.replace(marker, f"{marker}\n{emphasis}", 1)
    ElementTree.fromstring(svg)
    return svg


def main() -> None:
    args = _args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    svg = render(args.smiles, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()

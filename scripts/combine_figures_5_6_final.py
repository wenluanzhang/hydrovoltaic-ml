"""Combine validated Figure 5 and Figure 6 panel files without changing them."""

from __future__ import annotations

import copy
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

FIGURES = {
    "fig5": {
        "directory": ROOT / "results/figure5_R_origin/final_panels",
        "panels": [("A", "fig5A_final_electrolyte_condition_vs_R"),
                   ("B", "fig5B_final_ion_type_vs_R"),
                   ("C", "fig5C_final_structure_class_vs_R")],
        "columns": 3,
        "page_width": 776.0,
        "gap_x": 10.0,
        "gap_y": 10.0,
    },
    "fig6": {
        "directory": ROOT / "results/figure6_virtual_design/final_panels",
        "panels": [("A", "fig6A_final_explicit_descriptor_model"),
                   ("B", "fig6B_final_linear_vs_polynomial_descriptor_model"),
                   ("C", "fig6C_final_regime_aware_virtual_design_map"),
                   ("D", "fig6D_final_ranked_virtual_descriptor_combinations")],
        "columns": 2,
        "page_width": 786.0,
        "gap_x": 12.0,
        "gap_y": 12.0,
    },
}
MARGIN = 8.0
LABEL_HEIGHT = 17.0
LABEL_SIZE = 12.5


def dimensions(path: Path) -> tuple[float, float]:
    view = ET.parse(path).getroot().attrib["viewBox"].split()
    return float(view[2]), float(view[3])


def prefix_ids(root: ET.Element, prefix: str) -> None:
    mapping = {e.attrib["id"]: f"{prefix}_{e.attrib['id']}" for e in root.iter() if "id" in e.attrib}
    for e in root.iter():
        for key, value in list(e.attrib.items()):
            for old, new in mapping.items():
                value = value.replace(f"url(#{old})", f"url(#{new})")
                if value == f"#{old}":
                    value = f"#{new}"
            e.attrib[key] = value
        if "id" in e.attrib:
            e.attrib["id"] = mapping[e.attrib["id"]]


def geometry(spec: dict) -> tuple[list[dict], float, float]:
    panels = []
    columns = spec["columns"]
    for label, stem in spec["panels"]:
        width, height = dimensions(spec["directory"] / f"{stem}.svg")
        panels.append({"label": label, "stem": stem, "width": width, "height": height, "scale": 1.0})
    # Use one scale per composite. This prevents wide native canvases (notably
    # Fig. 5C and Fig. 6D) from receiving smaller fonts than their neighbors.
    column_widths = [max(panels[i]["width"] for i in range(col, len(panels), columns)) for col in range(columns)]
    rows = (len(panels) + columns - 1) // columns
    row_heights = [LABEL_HEIGHT + max(panels[i]["height"] * panels[i]["scale"] for i in range(r * columns, min((r + 1) * columns, len(panels)))) for r in range(rows)]
    page_height = 2 * MARGIN + sum(row_heights) + (rows - 1) * spec["gap_y"]
    tops = []
    y = MARGIN
    for h in row_heights:
        tops.append(y)
        y += h + spec["gap_y"]
    for i, panel in enumerate(panels):
        row, col = divmod(i, columns)
        panel["x"] = MARGIN + sum(column_widths[:col]) + col * spec["gap_x"]
        panel["label_y"] = tops[row] + LABEL_SIZE
        panel["y"] = tops[row] + LABEL_HEIGHT
    return panels, spec["page_width"], page_height


def write_svg(spec: dict, panels: list[dict], page_width: float, page_height: float, output: Path) -> None:
    root = ET.Element(f"{{{SVG_NS}}}svg", {"width": f"{page_width:.3f}pt", "height": f"{page_height:.3f}pt", "viewBox": f"0 0 {page_width:.3f} {page_height:.3f}", "version": "1.1"})
    for panel in panels:
        source = ET.parse(spec["directory"] / f"{panel['stem']}.svg").getroot()
        prefix_ids(source, panel["label"])
        group = ET.SubElement(root, f"{{{SVG_NS}}}g", {"transform": f"translate({panel['x']:.3f} {panel['y']:.3f}) scale({panel['scale']:.8f})"})
        for child in list(source):
            group.append(copy.deepcopy(child))
        label = ET.SubElement(root, f"{{{SVG_NS}}}text", {"x": f"{panel['x']:.3f}", "y": f"{panel['label_y']:.3f}", "style": "font-family: Arial, Helvetica, sans-serif; font-size: 12.5px; font-weight: 700; fill: #000000;"})
        label.text = panel["label"]
    ET.ElementTree(root).write(output, encoding="utf-8", xml_declaration=True)


def write_pdf(spec: dict, panels: list[dict], page_width: float, page_height: float, output: Path) -> None:
    font = Path(r"C:\Windows\Fonts\arialbd.ttf")
    font_name = "Helvetica-Bold"
    if font.exists():
        pdfmetrics.registerFont(TTFont("Arial-Bold-Composite", str(font)))
        font_name = "Arial-Bold-Composite"
    stream = BytesIO()
    c = canvas.Canvas(stream, pagesize=(page_width, page_height))
    c.setFont(font_name, LABEL_SIZE)
    for panel in panels:
        c.drawString(panel["x"], page_height - panel["label_y"], panel["label"])
    c.save()
    destination = PdfReader(BytesIO(stream.getvalue())).pages[0]
    for panel in panels:
        source = PdfReader(spec["directory"] / f"{panel['stem']}.pdf").pages[0]
        h = float(source.mediabox.height)
        destination.merge_transformed_page(source, Transformation().scale(panel["scale"]).translate(panel["x"], page_height - panel["y"] - h * panel["scale"]))
    writer = PdfWriter(); writer.add_page(destination)
    with output.open("wb") as handle:
        writer.write(handle)


def write_png(spec: dict, pdf: Path, output: Path) -> None:
    temp_root = ROOT / "tmp" / "pdfs"; temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="combined_", dir=temp_root) as d:
        prefix = Path(d) / output.stem
        subprocess.run(["pdftoppm", "-r", "600", "-png", "-singlefile", str(pdf), str(prefix)], check=True)
        shutil.copyfile(prefix.with_suffix(".png"), output)


def main() -> None:
    for name, spec in FIGURES.items():
        panels, width, height = geometry(spec)
        directory = spec["directory"]; stem = f"{name}_combined_final"
        svg, pdf, png = directory / f"{stem}.svg", directory / f"{stem}.pdf", directory / f"{stem}.png"
        write_svg(spec, panels, width, height, svg); write_pdf(spec, panels, width, height, pdf); write_png(spec, pdf, png)
        print(f"Saved {svg}\nSaved {pdf}\nSaved {png}")


if __name__ == "__main__":
    main()

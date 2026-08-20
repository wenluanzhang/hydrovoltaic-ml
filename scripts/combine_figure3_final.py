"""Assemble the validated Figure 3 panels into a vector 2x2 composite.

The source SVG/PDF panels are read-only. This layout-only compositor prefixes
SVG identifiers before nesting each panel, adds one exterior panel label per
panel, and preserves the panel PDFs as vector objects in the combined PDF.
"""

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


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PANEL_DIR = PROJECT_ROOT / "results" / "figure3_model_comparison" / "final_panels"
PANELS = [
    ("A", "fig3A_final_tuned_model_comparison"),
    ("B", "fig3B_final_descriptor_augmentation"),
    ("C", "fig3C_final_feature_block_ablation"),
    ("D", "fig3D_final_SHAP_descriptor_importance"),
]
OUT_BASENAME = "fig3_combined_final"

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)

PAGE_WIDTH = 540.0
OUTER_MARGIN = 6.0
COLUMN_GAP = 8.0
ROW_GAP = 10.0
LABEL_HEIGHT = 18.0
LABEL_FONT_SIZE = 12.5


def svg_dimensions(path: Path) -> tuple[float, float]:
    root = ET.parse(path).getroot()
    _, _, width, height = (float(value) for value in root.attrib["viewBox"].split())
    return width, height


def prefix_svg_ids(root: ET.Element, prefix: str) -> None:
    """Avoid clip-path and marker collisions in the nested SVG panels."""
    id_map = {
        element.attrib["id"]: f"{prefix}_{element.attrib['id']}"
        for element in root.iter()
        if "id" in element.attrib
    }
    for element in root.iter():
        for attribute, value in list(element.attrib.items()):
            for old, new in id_map.items():
                value = value.replace(f"url(#{old})", f"url(#{new})")
                if value == f"#{old}":
                    value = f"#{new}"
            element.attrib[attribute] = value
        if "id" in element.attrib:
            element.attrib["id"] = id_map[element.attrib["id"]]


def panel_geometry() -> tuple[list[dict[str, object]], float, float]:
    cell_width = (PAGE_WIDTH - 2 * OUTER_MARGIN - COLUMN_GAP) / 2
    panels: list[dict[str, object]] = []
    for label, stem in PANELS:
        width, height = svg_dimensions(PANEL_DIR / f"{stem}.svg")
        scale = cell_width / width
        panels.append({"label": label, "stem": stem, "width": width, "height": height, "scale": scale})

    row_heights = [
        LABEL_HEIGHT + max(float(panel["height"]) * float(panel["scale"]) for panel in panels[:2]),
        LABEL_HEIGHT + max(float(panel["height"]) * float(panel["scale"]) for panel in panels[2:]),
    ]
    page_height = 2 * OUTER_MARGIN + sum(row_heights) + ROW_GAP
    row_tops = [OUTER_MARGIN, OUTER_MARGIN + row_heights[0] + ROW_GAP]
    column_lefts = [OUTER_MARGIN, OUTER_MARGIN + cell_width + COLUMN_GAP]

    for index, panel in enumerate(panels):
        row, column = divmod(index, 2)
        panel["x"] = column_lefts[column]
        panel["label_y"] = row_tops[row] + LABEL_FONT_SIZE
        panel["y"] = row_tops[row] + LABEL_HEIGHT
    return panels, PAGE_WIDTH, page_height


def write_combined_svg(panels: list[dict[str, object]], page_width: float, page_height: float) -> Path:
    root = ET.Element(
        f"{{{SVG_NS}}}svg",
        {
            "width": f"{page_width:.3f}pt",
            "height": f"{page_height:.3f}pt",
            "viewBox": f"0 0 {page_width:.3f} {page_height:.3f}",
            "version": "1.1",
        },
    )
    for panel in panels:
        source_root = ET.parse(PANEL_DIR / f"{panel['stem']}.svg").getroot()
        prefix_svg_ids(source_root, str(panel["label"]))
        group = ET.SubElement(
            root,
            f"{{{SVG_NS}}}g",
            {
                "transform": (
                    f"translate({float(panel['x']):.3f} {float(panel['y']):.3f}) "
                    f"scale({float(panel['scale']):.8f})"
                )
            },
        )
        for child in list(source_root):
            group.append(copy.deepcopy(child))
        label = ET.SubElement(
            root,
            f"{{{SVG_NS}}}text",
            {
                "x": f"{float(panel['x']):.3f}",
                "y": f"{float(panel['label_y']):.3f}",
                "style": "font-family: Arial, Helvetica, sans-serif; font-size: 12.5px; font-weight: 700; fill: #000000;",
            },
        )
        label.text = str(panel["label"])

    output = PANEL_DIR / f"{OUT_BASENAME}.svg"
    ET.ElementTree(root).write(output, encoding="utf-8", xml_declaration=True)
    return output


def register_panel_label_font() -> str:
    arial_bold = Path(r"C:\Windows\Fonts\arialbd.ttf")
    if arial_bold.exists():
        pdfmetrics.registerFont(TTFont("Arial-Bold", str(arial_bold)))
        return "Arial-Bold"
    return "Helvetica-Bold"


def write_combined_pdf(panels: list[dict[str, object]], page_width: float, page_height: float) -> Path:
    font_name = register_panel_label_font()
    label_stream = BytesIO()
    label_canvas = canvas.Canvas(label_stream, pagesize=(page_width, page_height))
    label_canvas.setFont(font_name, LABEL_FONT_SIZE)
    for panel in panels:
        label_canvas.drawString(
            float(panel["x"]),
            page_height - float(panel["label_y"]),
            str(panel["label"]),
        )
    label_canvas.save()

    destination = PdfReader(BytesIO(label_stream.getvalue())).pages[0]
    for panel in panels:
        source = PdfReader(PANEL_DIR / f"{panel['stem']}.pdf").pages[0]
        source_height = float(source.mediabox.height)
        destination.merge_transformed_page(
            source,
            Transformation()
            .scale(float(panel["scale"]))
            .translate(
                float(panel["x"]),
                page_height - float(panel["y"]) - source_height * float(panel["scale"]),
            ),
        )

    output = PANEL_DIR / f"{OUT_BASENAME}.pdf"
    writer = PdfWriter()
    writer.add_page(destination)
    with output.open("wb") as handle:
        writer.write(handle)
    return output


def write_png(pdf_path: Path) -> Path:
    temp_root = PROJECT_ROOT / "tmp" / "pdfs"
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="fig3_combined_", dir=temp_root) as temp_dir:
        prefix = Path(temp_dir) / OUT_BASENAME
        subprocess.run(
            ["pdftoppm", "-r", "600", "-png", "-singlefile", str(pdf_path), str(prefix)],
            check=True,
        )
        output = PANEL_DIR / f"{OUT_BASENAME}.png"
        shutil.copyfile(prefix.with_suffix(".png"), output)
    return output


def main() -> None:
    panels, page_width, page_height = panel_geometry()
    svg_path = write_combined_svg(panels, page_width, page_height)
    pdf_path = write_combined_pdf(panels, page_width, page_height)
    png_path = write_png(pdf_path)
    print(f"Saved: {svg_path}")
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")


if __name__ == "__main__":
    main()

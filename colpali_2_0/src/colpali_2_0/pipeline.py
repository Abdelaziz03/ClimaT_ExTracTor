from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .extract import extract_document
from .schema import DocumentExtraction, Element


Row = dict[str, object | None]


def _rgb_to_hex(color: tuple[float, float, float] | None) -> str | None:
    if color is None:
        return None
    r, g, b = (max(0, min(255, round(c * 255))) for c in color)
    return f"#{r:02X}{g:02X}{b:02X}"


def _element_rows(source_pdf: str, elements: list[Element]) -> list[Row]:
    rows: list[Row] = []
    for e in elements:
        x0, y0, x1, y1 = e.bbox
        rows.append(
            {
                "source_pdf": source_pdf,
                "element_id": e.element_id,
                "page": e.page,
                "element_type": e.element_type,
                "text": e.text,
                "bbox_x0": x0,
                "bbox_y0": y0,
                "bbox_x1": x1,
                "bbox_y1": y1,
                "stroke_color": e.stroke_color,
                "stroke_hex": _rgb_to_hex(e.stroke_color),
                "fill_color": e.fill_color,
                "fill_hex": _rgb_to_hex(e.fill_color),
                "parent_id": e.parent_id,
                "children_count": len(e.children_ids),
            }
        )
    return rows


def _run_pipeline_extraction(
    extraction: DocumentExtraction, output_dir: str, output_prefix: str
) -> tuple[Path, Path, list[Row]]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / f"{output_prefix}.json"
    csv_path = out_dir / f"{output_prefix}_table.csv"

    json_path.write_text(json.dumps(extraction.model_dump(), indent=2), encoding="utf-8")

    rows = _element_rows(extraction.source_pdf, extraction.elements)
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    return json_path, csv_path, rows


def run_pipeline(pdf_path: str, output_dir: str, output_prefix: str | None = None) -> tuple[Path, Path]:
    extraction = extract_document(pdf_path)
    stem = output_prefix or Path(pdf_path).stem
    json_path, csv_path, _ = _run_pipeline_extraction(extraction, output_dir, stem)
    return json_path, csv_path


def discover_pdfs(pdf_dir: str, recursive: bool = False) -> list[Path]:
    directory = Path(pdf_dir)
    if not directory.exists() or not directory.is_dir():
        raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")

    files = directory.rglob("*") if recursive else directory.iterdir()
    pdf_paths = sorted(p for p in files if p.is_file() and p.suffix.lower() == ".pdf")
    if not pdf_paths:
        raise ValueError(f"No PDF files found in: {pdf_dir}")
    return pdf_paths


def run_pipeline_for_directory(
    pdf_dir: str,
    output_dir: str,
    recursive: bool = False,
    write_combined_table: bool = True,
) -> list[tuple[Path, Path]]:
    outputs: list[tuple[Path, Path]] = []
    all_rows: list[Row] = []

    root = Path(pdf_dir)
    for pdf_path in discover_pdfs(pdf_dir, recursive=recursive):
        rel = pdf_path.relative_to(root)
        stem = rel.with_suffix("").as_posix().replace("/", "__")
        extraction = extract_document(str(pdf_path))
        json_path, csv_path, rows = _run_pipeline_extraction(extraction, output_dir, stem)
        outputs.append((json_path, csv_path))
        all_rows.extend(rows)

    if write_combined_table and all_rows:
        combined_path = Path(output_dir) / "combined_table.csv"
        pd.DataFrame(all_rows).to_csv(combined_path, index=False)

    return outputs

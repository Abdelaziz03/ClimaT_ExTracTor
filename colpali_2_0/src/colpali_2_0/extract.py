from __future__ import annotations

from dataclasses import dataclass

import fitz

from .schema import DocumentExtraction, Element


@dataclass
class RawElement:
    element_id: str
    page: int
    element_type: str
    bbox: tuple[float, float, float, float]
    text: str | None = None
    stroke_color: tuple[float, float, float] | None = None
    fill_color: tuple[float, float, float] | None = None


def _as_rgb(color: tuple[float, ...] | int | None) -> tuple[float, float, float] | None:
    if color is None:
        return None
    if isinstance(color, int):
        r = ((color >> 16) & 255) / 255
        g = ((color >> 8) & 255) / 255
        b = (color & 255) / 255
        return (r, g, b)
    if isinstance(color, tuple):
        if len(color) >= 3:
            return (float(color[0]), float(color[1]), float(color[2]))
    return None


def _contains(outer: tuple[float, float, float, float], inner: tuple[float, float, float, float]) -> bool:
    ox0, oy0, ox1, oy1 = outer
    ix0, iy0, ix1, iy1 = inner
    return ox0 <= ix0 and oy0 <= iy0 and ox1 >= ix1 and oy1 >= iy1


def _box_area(box: tuple[float, float, float, float]) -> float:
    x0, y0, x1, y1 = box
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def _assign_hierarchy(elements: list[RawElement]) -> dict[str, dict[str, str | list[str] | None]]:
    by_id = {e.element_id: {"parent_id": None, "children_ids": []} for e in elements}
    for child in elements:
        candidates: list[RawElement] = []
        for parent in elements:
            if child.element_id == parent.element_id:
                continue
            if child.page != parent.page:
                continue
            if _contains(parent.bbox, child.bbox):
                candidates.append(parent)
        if candidates:
            smallest_parent = min(candidates, key=lambda e: _box_area(e.bbox))
            by_id[child.element_id]["parent_id"] = smallest_parent.element_id
            by_id[smallest_parent.element_id]["children_ids"].append(child.element_id)
    return by_id


def extract_document(pdf_path: str) -> DocumentExtraction:
    doc = fitz.open(pdf_path)
    elements: list[RawElement] = []

    for page_index, page in enumerate(doc):
        text_blocks = page.get_text("blocks")
        for block_idx, block in enumerate(text_blocks):
            x0, y0, x1, y1, text, *_ = block
            cleaned = text.strip() if text else ""
            if not cleaned:
                continue
            elements.append(
                RawElement(
                    element_id=f"p{page_index}_t{block_idx}",
                    page=page_index,
                    element_type="text",
                    bbox=(float(x0), float(y0), float(x1), float(y1)),
                    text=cleaned,
                )
            )

        drawings = page.get_drawings()
        for draw_idx, drawing in enumerate(drawings):
            rect = drawing.get("rect")
            if rect is None:
                continue
            elements.append(
                RawElement(
                    element_id=f"p{page_index}_b{draw_idx}",
                    page=page_index,
                    element_type="box",
                    bbox=(float(rect.x0), float(rect.y0), float(rect.x1), float(rect.y1)),
                    stroke_color=_as_rgb(drawing.get("color")),
                    fill_color=_as_rgb(drawing.get("fill")),
                )
            )

    hierarchy = _assign_hierarchy(elements)
    typed_elements = [
        Element(
            element_id=e.element_id,
            page=e.page,
            element_type=e.element_type,
            text=e.text,
            bbox=e.bbox,
            stroke_color=e.stroke_color,
            fill_color=e.fill_color,
            parent_id=hierarchy[e.element_id]["parent_id"],
            children_ids=hierarchy[e.element_id]["children_ids"],
        )
        for e in elements
    ]
    return DocumentExtraction(source_pdf=pdf_path, elements=typed_elements)

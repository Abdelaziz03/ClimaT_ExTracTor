from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


ElementType = Literal["text", "box"]


class Element(BaseModel):
    element_id: str
    page: int
    element_type: ElementType
    text: str | None = None
    bbox: tuple[float, float, float, float]
    stroke_color: tuple[float, float, float] | None = None
    fill_color: tuple[float, float, float] | None = None
    parent_id: str | None = None
    children_ids: list[str] = Field(default_factory=list)


class DocumentExtraction(BaseModel):
    source_pdf: str
    elements: list[Element]

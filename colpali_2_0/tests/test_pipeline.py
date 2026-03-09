from pathlib import Path

import pytest

from colpali_2_0.pipeline import discover_pdfs


def test_discover_pdfs_returns_only_pdf_files(tmp_path: Path) -> None:
    (tmp_path / "a.pdf").write_bytes(b"%PDF-1.4")
    (tmp_path / "b.PDF").write_bytes(b"%PDF-1.4")
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")

    found = discover_pdfs(str(tmp_path))

    assert [p.name for p in found] == ["a.pdf", "b.PDF"]


def test_discover_pdfs_raises_for_empty_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="No PDF files found"):
        discover_pdfs(str(tmp_path))


def test_discover_pdfs_recursive_finds_nested_pdfs(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "inner.pdf").write_bytes(b"%PDF-1.4")

    found = discover_pdfs(str(tmp_path), recursive=True)

    assert [p.name for p in found] == ["inner.pdf"]

from __future__ import annotations

import argparse

from .llm import describe_local_llm
from .pipeline import run_pipeline, run_pipeline_for_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Colpali 2.0 PDF extraction pipeline")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pdf", help="Path to one input PDF")
    group.add_argument("--pdf-dir", help="Directory containing input PDFs")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--recursive", action="store_true", help="Recursively scan --pdf-dir for PDFs")
    parser.add_argument(
        "--no-combined-table",
        action="store_true",
        help="Do not write combined_table.csv when processing --pdf-dir",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    print(describe_local_llm())
    if args.pdf:
        json_path, csv_path = run_pipeline(args.pdf, args.out)
        print(f"JSON output: {json_path}")
        print(f"Table output: {csv_path}")
        return

    outputs = run_pipeline_for_directory(
        args.pdf_dir,
        args.out,
        recursive=args.recursive,
        write_combined_table=not args.no_combined_table,
    )
    for json_path, csv_path in outputs:
        print(f"JSON output: {json_path}")
        print(f"Table output: {csv_path}")


if __name__ == "__main__":
    main()

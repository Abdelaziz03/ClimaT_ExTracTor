# Colpali 2.0

`Colpali 2.0` is a local-first PDF understanding pipeline inspired by the ColPali architecture style (document layout + semantic retrieval), adapted for fully local execution with a medium-sized LLM (for example, **Mistral 7B Instruct** served through Ollama or llama.cpp).

## What it does

1. **PDF input**: reads one PDF or a folder of PDFs.
2. **JSON transformation (without deleting PDF)**: creates structured JSON metadata while keeping original PDFs untouched.
3. **Architecture/layout extraction**:
   - detects text blocks and graphical boxes,
   - computes hierarchy between boxes using geometric containment,
   - extracts box color (stroke/fill when available).
4. **Tabular output**: exports flattened rows as CSV for analytics.

## Proposed architecture

- `extract.py`: text blocks, drawing objects, colors, and hierarchy extraction.
- `schema.py`: data models for JSON and table exports.
- `pipeline.py`: orchestrates single-file and folder processing flows.
- `llm.py`: local LLM adapter (Mistral 7B by default) for future semantic enrichment.

## Quick start

```bash
cd colpali_2_0
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Process one PDF

```bash
python -m colpali_2_0.cli --pdf /path/to/input.pdf --out ./output
```

### Process all PDFs in a folder (e.g., your future `test/` folder)

```bash
python -m colpali_2_0.cli --pdf-dir ./test --out ./output
```

### Process nested folders recursively

```bash
python -m colpali_2_0.cli --pdf-dir ./test --recursive --out ./output
```

## Outputs

For each input PDF `name.pdf`, output directory contains:

- `name.json`: full structured extraction.
- `name_table.csv`: flattened tabular view of detected elements.
- `combined_table.csv`: combined rows for all PDFs in folder mode (can disable with `--no-combined-table`).
- Original PDF remains unchanged.

In folder mode with nested paths, file names are de-conflicted using path prefixes (for example, `subdir__name.json`).

## Notes on local LLM

The extraction pipeline does not require an online model. If semantic post-processing is enabled later, use a local model such as:

- `mistral:7b-instruct` (Ollama)
- `Qwen2.5-7B-Instruct` (llama.cpp-compatible GGUF)

These are medium-sized models and usually a practical fit for local hardware.

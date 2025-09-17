# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project: SnapShotPlot

Summary
- Python package to capture code and visualizations (matplotlib, Plotly, Altair) and generate timestamped artifacts (code, plot, docs). Supports multiple export formats, Jupyter magics, a static site generator, and an optional search index.

Environment
- Python >= 3.9
- Install for development: pip install -e ".[dev]"
- Optional extras: [jupyter], [site], [cli], [academic], [all]

Core commands
- Setup (recommended on macOS)
  - python -m venv .venv
  - source .venv/bin/activate
  - pip install -e ".[dev]"

- Tests
  - Run all: pytest
  - With coverage: pytest --cov=snapshotplot
  - Single file: pytest tests/test_snapshot.py -q
  - Single test: pytest tests/test_snapshot.py::TestTimestamp::test_timestamp_generation -q

- Lint/format/type-check
  - Format: black snapshotplot/ tests/
  - Lint: flake8 snapshotplot tests
  - Types: mypy snapshotplot

- CLI (installed via console_script "snapshotplot")
  - Initialize a site: snapshotplot init my-plot-site --template scientific --author "Your Name" --title "My Plots"
  - Create a collection: snapshotplot collection create experiments --title "Experiments"
  - Build site: snapshotplot build
  - Serve locally: snapshotplot serve --host 127.0.0.1 --port 8000
  - Deploy to GitHub Pages: snapshotplot deploy -m "Update plots" --push
  - List plots (after building/adding collections): snapshotplot list --collection experiments

- Library usage (minimal examples)
  - Decorator: from snapshotplot import snapshot; @snapshot(title="My Plot")
  - Context manager: from snapshotplot import snapshot; with snapshot(title="My Plot"): ...
  - Jupyter magics: %load_ext snapshotplot then use %%snapshot ...
  - Plot formats: @snapshot(backend='plotly', plot_formats=['html','png']) to control saved plot files per backend

Key architecture
- snapshotplot/core
  - snapshot.py
    - SnapshotContext: Orchestrates a snapshot run with a single global timestamp per run (timestamp.get_current_timestamp). Steps:
      1) Discover caller and source via code_capture.get_calling_info
      2) Create output folder via file_manager.create_output_directory under snapshots/snapshot_<filename>
      3) Save source; detect and save plot(s) via a visualization backend
      4) Export documentation in requested formats (html/pdf/markdown/jupyter/latex) via export_formats.ExportFormatRegistry
      5) Optionally index into SQLite if enable_search=True (search_system)
      6) Optional site integration (copy artifacts and write metadata under a site/collection), auto-commit/build/deploy if configured
    - SnapshotDecorator and snapshot(...) helper expose both decorator and context manager APIs.
  - visualization_backends.py
    - Pluggable backend system. Implementations:
      - MatplotlibBackend: default; saves current figure to <timestamp>_plot.png (and other formats when requested)
      - PlotlyBackend: locates go.Figure objects in caller context; can save html/png/svg/pdf/json
      - AltairBackend: locates alt.Chart objects; can save html/png/svg/pdf/json
  - export_formats.py
    - ExportContext carries code, plot paths, metadata, timestamp, output_dir
    - Formats:
      - HTMLExportFormat: uses core/html_writer.py to render an HTML report
      - PDFExportFormat: renders HTML to PDF with WeasyPrint
      - MarkdownExportFormat: Markdown with YAML front matter and embedded plots
      - JupyterNotebookExportFormat: emits an .ipynb with code and embedded plot outputs
      - LaTeXExportFormat: TeX with code listing and figures
  - html_writer.py
    - Generates dark-themed HTML with syntax-highlighted code (Pygments) and plot preview
  - code_capture.py
    - Introspects the call stack to extract function name, file, and source code (falls back gracefully)
  - file_manager.py
    - Snapshot folder naming and output file paths: <timestamp>_code.py, <timestamp>_plot.png, <timestamp>_snapshot.html
  - timestamp.py
    - Global per-run timestamp and datetime helpers
  - search_system.py
    - SQLite-based index with FTS5 for full-text search across code/metadata; tags stored in a separate table

- snapshotplot/jupyter
  - jupyter_integration.py
    - IPython magics:
      - Line magic %snapshot (captures previous cell output)
      - Cell magic %%snapshot (executes cell then captures)
    - notebook_snapshot(...) detects notebook context and augments SnapshotContext metadata

- snapshotplot/site
  - site_generator.py
    - Builds a static site into docs/ using templates from core/templates.py
    - Collections live under collections/<name>/<timestamp_title>/ with index.md front matter and copied artifacts

- snapshotplot/cli
  - cli/cli.py (exposed as the snapshotplot command)
    - init: scaffold a site directory structure, templates, basic workflow
    - collection create: add collections with index metadata
    - build/serve/deploy/list: manage the site lifecycle locally and on GitHub Pages

Conventions and defaults
- Default snapshot output root: snapshots/ (created in CWD)
- Snapshot directory: snapshots/snapshot_<source_filename_without_ext>/
- Default export_formats=['html'] unless overridden; set enable_search=True to index snapshots (no extra install needed)
- Plot file formats: default ['png']; configure via plot_formats per backend
- CLI build output: docs/

References from README.md (essentials)
- Dev install: pip install -e ".[dev]"
- Run tests: pytest
- Code format: black snapshotplot/
- Optional installs by workflow: snapshotplot[jupyter], snapshotplot[site], snapshotplot[all]

Notes for Warp
- Prefer pytest -q -k ... to target a subset quickly
- When invoking CLI in CI or scripts, ensure the package is installed (pip install -e . or pip install snapshotplot)
- Do not assume Jupyter extras are present unless snapshotplot[jupyter] was installed

# SKOLLR

SKOLLR is a lightweight desktop helper for working with Canvas LMS data and quick course insights. It provides a small UI, Canvas API integration, and optional AI-powered analysis to produce study tips and task summaries.

This repository is a development workspace — the app is run locally via `main.py` and uses the files under `src/` for core functionality.

## Quick Start

- Requirements: Python 3.10+. See `requirements.txt`.
- Recommended: use a virtual environment.

Install dependencies and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

If you prefer not to use a venv, ensure you have the packages from `requirements.txt` installed globally.

## Configuration / API Keys

The app needs access to your Canvas instance and (optionally) an AI provider for analysis. You can provide credentials either via a `.env` file in the repository root or using the app's API key dialog (`src/ui/api_key_dialog.py`).

Create a `.env` file with values like:

```ini
CANVAS_BASE_URL=https://your-school.instructure.com
CANVAS_API_TOKEN=your_canvas_token_here
GEMINI_API_KEY=your_gemini_key_here   # optional, for AI features
```

Notes:

- `CANVAS_API_TOKEN` is typically generated in Canvas under Account → Settings → New Access Token.
- If you don't provide `GEMINI_API_KEY`, AI features (in `src/ai/gemini.py`) will be disabled.

## Project Structure

- `main.py` — application entry point.
- `requirements.txt` — Python dependencies.
- `src/`
  - `ai/gemini.py` — AI helpers (Gemini integration).
  - `api/canvas_api.py` — Canvas API wrapper and data fetchers.
  - `ui/` — PySide6 UI modules: `dashboard.py`, `course_details.py`, `api_key_dialog.py`, `graphs.py`, `settings.py`, `analysis.py`.
  - `utils/data_transformer.py` — data normalization and helpers.

## Usage Notes

- Launch the UI with `python main.py`.
- The dashboard shows courses and upcoming assignments. Click a course to view details and generated insights.
- Use the API key dialog in the UI to add or update your Canvas token without editing files.

## Development

- Run the app from the project root so relative imports resolve correctly.
  Example local run for development:

```bash
source .venv/bin/activate
python main.py
```

## License

This project is available under the terms in the `LICENSE` file in this repository.

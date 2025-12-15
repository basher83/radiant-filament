---
name: require-uv
enabled: true
event: bash
pattern: ^(python3?|pip3?)\s|mise\s+exec\s+(python3?|pip3?)
action: block
---

**Direct Python/pip command blocked**

This project uses `uv` for Python package and environment management. Do not use `python`, `python3`, `pip`, or `pip3` directly (or via `mise exec`).

**Use these instead:**

| Instead of | Use |
|------------|-----|
| `python script.py` | `uv run script.py` |
| `python3 script.py` | `uv run script.py` |
| `pip install package` | `uv add package` |
| `pip3 install package` | `uv add package` |
| `python -m pytest` | `uv run pytest` |
| `pip install -r requirements.txt` | `uv sync` |
| `mise exec python -- script.py` | `uv run script.py` |

**Why uv?**

- Consistent, reproducible environments
- Faster dependency resolution
- Project-level virtual environment management

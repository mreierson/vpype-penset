# Contributing to vpype-penset

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Checks

```bash
pytest
python -m build
```

If you have `ruff` and `mypy` installed through the `dev` extra, run:

```bash
ruff check src tests
mypy src
```

## Guidelines

- Keep the public API small and well documented.
- Add tests for new pen sets, parsing rules, or command behavior.
- Update the README, docs, and changelog when CLI behavior changes.
- Preserve compatibility with vpype 1.14+ unless a version bump is intentional.

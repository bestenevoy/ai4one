# AI4One

This is a small package for machine learning.

## Installation

Install AI4One using pip:

```bash
pip install ai4one
```

Ensure you have Python 3.8+ and pip installed.

## Develop

```bash
uv pip install -e ".[dev]"
uv run -m pytest
```

## Build

```
uv build
```

## Publish to PyPI

```
python -m twine upload dist/*
uv run twine upload dist/*
```

## Testing and Local Updates
For development or testing, synchronize your local environment with:

```
uv sync
```

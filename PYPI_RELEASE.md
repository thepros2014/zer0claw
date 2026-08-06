# PyPI Release Instructions

This document explains how to set up the **new standalone Python project** for publishing `zeroclaw-commerce` to PyPI.

---

## 1. Files to copy from this repo

Copy these into your new project root (rename directories as shown):

| Source (this repo)       | Destination (new project)  |
|--------------------------|----------------------------|
| `fastapi-gateway/`       | `zeroclaw_gateway/`        |
| `telegram-bot/`          | `zeroclaw_bot/`            |
| `download_model.py`      | `download_model.py`        |
| `README.md`              | `README.md`                |
| `docs/`                  | `docs/`                    |
| `pyproject.toml`         | `pyproject.toml` ✅ (ready) |
| `MANIFEST.in`            | `MANIFEST.in` ✅ (ready)   |

---

## 2. Add `__init__.py` files

```
zeroclaw_gateway/__init__.py   (empty file)
zeroclaw_bot/__init__.py       (empty file)
```

---

## 3. New project directory structure

```
zeroclaw-commerce/          ← new GitHub repo root
├── zeroclaw_gateway/
│   ├── __init__.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── solana.py
│   │   └── static/
│   │       ├── index.html
│   │       └── setup.html
│   ├── requirements.txt
│   └── tests/
│       └── test_gateway.py
├── zeroclaw_bot/
│   ├── __init__.py
│   ├── bot.py
│   ├── requirements.txt
│   └── README.md
├── download_model.py
├── README.md
├── pyproject.toml
├── MANIFEST.in
└── docs/
```

---

## 4. Build and upload to PyPI

```bash
# Install build tools
pip install build twine

# Build the distribution
python -m build

# Upload to PyPI (requires PyPI account + API token)
twine upload dist/*
```

To upload to **TestPyPI** first (recommended):

```bash
twine upload --repository testpypi dist/*
```

---

## 5. Configure PyPI API token

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi

[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE
```

Or pass via environment variable:

```bash
TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-YOUR_TOKEN twine upload dist/*
```

---

## 6. Install from PyPI (after publishing)

```bash
pip install zeroclaw-commerce
```

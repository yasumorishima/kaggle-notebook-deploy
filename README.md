# kaggle-notebook-deploy

A CLI tool to deploy Kaggle Notebooks by simply running `git push`.

Manage your Kaggle Notebook code on GitHub and set up an automated deployment workflow via GitHub Actions.

## Workflow

```
Edit notebook → git push → GitHub Actions → Upload to Kaggle → Submit in browser
```

## Installation

```bash
pip install kaggle-notebook-deploy
```

## Quick Start

### 1. Set up repository

```bash
# Generate GitHub Actions workflow and .gitignore
kaggle-notebook-deploy init-repo
```

Generated files:
- `.github/workflows/kaggle-push.yml` — workflow for pushing to Kaggle
- `scripts/setup-credentials.sh` — credential setup script
- `.gitignore` entries for Kaggle-related files

### 2. Set GitHub Secrets

```bash
gh secret set KAGGLE_USERNAME
gh secret set KAGGLE_KEY
```

### 3. Create a competition directory

```bash
# Basic
kaggle-notebook-deploy init titanic

# GPU-enabled, public notebook
kaggle-notebook-deploy init march-machine-learning-mania-2026 --gpu --public
```

Generated files:
- `<slug>/kernel-metadata.json` — Kaggle kernel metadata
- `<slug>/<slug>-baseline.ipynb` — baseline notebook

### 4. Develop and deploy

```bash
# Edit the notebook
vim titanic/titanic-baseline.ipynb

# Validate
kaggle-notebook-deploy validate titanic

# Push directly from local
kaggle-notebook-deploy push titanic

# Or via GitHub Actions
git add titanic/ && git commit -m "Add titanic baseline" && git push
gh workflow run kaggle-push.yml -f notebook_dir=titanic
```

## Commands

### `kaggle-notebook-deploy init <competition-slug>`

Generate a competition directory from a template.

| Option | Description |
|---|---|
| `-u, --username` | Kaggle username (default: read from `~/.kaggle/kaggle.json`) |
| `-t, --title` | Notebook title (default: auto-generated from slug) |
| `--gpu` | Enable GPU |
| `--internet` | Enable internet (not recommended for code competitions) |
| `--public` | Create as public notebook |

### `kaggle-notebook-deploy init-repo`

Set up GitHub Actions workflow and related files.

| Option | Description |
|---|---|
| `-f, --force` | Overwrite existing files |

### `kaggle-notebook-deploy validate [directory]`

Validate `kernel-metadata.json`.

Checks:
- Required fields exist
- `id` format is `username/slug`
- `code_file` exists on disk
- Valid values for `language` and `kernel_type`
- Consistency between `enable_internet` and `competition_sources`

### `kaggle-notebook-deploy push [directory]`

Push a notebook to Kaggle (internally runs `kaggle kernels push`).

| Option | Description |
|---|---|
| `--skip-validate` | Skip validation |
| `--dry-run` | Print the command without executing |

## Notes

### Code competition constraints

- `enable_internet: false` is required (setting it to `true` disables submission)
- API-based submit is not available — browser submit is required
- `kaggle kernels push` resets Kaggle Secrets bindings; re-attach W&B keys etc. via the web UI after each push

### Data path differences

| Source | Mount path |
|---|---|
| `competition_sources` | `/kaggle/input/competitions/<slug>/` |
| `dataset_sources` | `/kaggle/input/<slug>/` |

Note that `competition_sources` data is mounted under **`competitions/`** subdirectory, not directly under `/kaggle/input/`. Hardcoding `/kaggle/input/<slug>/` will cause `FileNotFoundError`.

**Recommended pattern** — auto-detect the data directory in your notebook:

```python
from pathlib import Path

INPUT_ROOT = Path('/kaggle/input')
# Find actual data location instead of hardcoding the path
DATA_DIR = None
for p in INPUT_ROOT.rglob('your-expected-file.csv'):
    DATA_DIR = p.parent
    break

if DATA_DIR is None:
    # Print structure for debugging
    for p in sorted(INPUT_ROOT.iterdir()):
        print(f'  {p.name}/')
        for sub in sorted(p.iterdir())[:5]:
            print(f'    {sub.name}')
    raise FileNotFoundError('Data directory not found.')
```

### NaN handling for missing feature columns

When building features, some columns may be entirely `NaN` (e.g., a ranking system not available for Women's tournaments). `fillna(median)` does not help when the median itself is `NaN`. Always chain a fallback:

```python
X = df[feat_cols].fillna(df[feat_cols].median()).fillna(0)
```

## License

MIT

# kaggle-notebook-deploy: Deploy Kaggle Notebooks with git push

## Introduction

Are you still editing Kaggle Notebooks directly in the browser editor?

With the browser editor, you can't use Git for version control, reviewing diffs is painful, and you can't use your preferred editor like VSCode.

**kaggle-notebook-deploy** is a CLI tool that sets up this entire workflow with a single command.

```
pip install kaggle-notebook-deploy
```

Using GitHub Actions, it **automatically deploys to Kaggle every time you run `git push`**.

## The Workflow

```
Edit notebook → git push → GitHub Actions → Upload to Kaggle → Submit in browser
```

1. Edit `.ipynb` locally or on any device
2. `git add && git commit && git push`
3. `gh workflow run kaggle-push.yml -f notebook_dir=<competition-name>`
4. GitHub Actions uploads the notebook via the Kaggle API
5. Open the Kaggle Notebook page in your browser and click "Submit to Competition"

## Setup (5 minutes)

### Step 1: Install kaggle-notebook-deploy

```bash
pip install kaggle-notebook-deploy
```

### Step 2: Prepare Kaggle API credentials

Get an API token from [Kaggle Account Settings](https://www.kaggle.com/settings) and place it at `~/.kaggle/kaggle.json`.

```bash
# Skip if you already use the Kaggle CLI
mkdir -p ~/.kaggle
echo '{"username":"your-username","key":"your-api-key"}' > ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

### Step 3: Initialize the repository

```bash
# Create a new repo (or use an existing one)
mkdir my-kaggle && cd my-kaggle && git init

# Set up GitHub Actions workflow
kaggle-notebook-deploy init-repo
```

The following files are auto-generated:

```
my-kaggle/
├── .github/workflows/
│   └── kaggle-push.yml          # Kaggle push workflow
├── scripts/
│   └── setup-credentials.sh     # Credential setup for CI / new devices
└── .gitignore                   # Excludes data files etc.
```

### Step 4: Set GitHub Secrets

After pushing to GitHub, register your Kaggle credentials in the repository Secrets.

```bash
# Using GitHub CLI
gh secret set KAGGLE_USERNAME
gh secret set KAGGLE_KEY
```

Or via GitHub Web UI: **Settings > Secrets and variables > Actions**.

## Usage

### Join a competition

```bash
# Create a competition directory (slug = the last part of the Kaggle competition URL)
kaggle-notebook-deploy init titanic
```

```
titanic/
├── kernel-metadata.json         # Kaggle kernel metadata
└── titanic-baseline.ipynb       # Baseline notebook
```

`kernel-metadata.json` is auto-generated with:

```json
{
  "id": "your-username/titanic-baseline",
  "title": "Titanic Baseline",
  "code_file": "titanic-baseline.ipynb",
  "language": "python",
  "kernel_type": "notebook",
  "is_private": "true",
  "enable_gpu": "false",
  "enable_internet": "false",
  "competition_sources": ["titanic"]
}
```

### Common options

```bash
# Enable GPU (for XGBoost, LightGBM, etc.)
kaggle-notebook-deploy init my-competition --gpu

# Public notebook (for portfolio / medal hunting)
kaggle-notebook-deploy init my-competition --public

# Custom title
kaggle-notebook-deploy init my-competition --title "My Awesome Approach"

# Explicit username
kaggle-notebook-deploy init my-competition --username your-username
```

### Validate before deploying

```bash
kaggle-notebook-deploy validate titanic
```

Checks:
- Required fields (`id`, `title`, `code_file`, etc.) exist
- `id` is in `username/slug` format
- The file specified in `code_file` exists on disk
- `language` and `kernel_type` are valid values
- `enable_internet` is not `true` for code competitions (warning)

### Deploy to Kaggle

```bash
# Push directly from local (with validation)
kaggle-notebook-deploy push titanic

# Skip validation
kaggle-notebook-deploy push titanic --skip-validate

# Dry run: show the command without executing
kaggle-notebook-deploy push titanic --dry-run
```

### Deploy via GitHub Actions

```bash
git add titanic/ && git commit -m "Update titanic baseline" && git push
gh workflow run kaggle-push.yml -f notebook_dir=titanic
```

Check execution status in the GitHub Actions log:

```bash
gh run list --workflow=kaggle-push.yml
gh run view <run-id> --log
```

### Check notebook execution status

```bash
kaggle kernels status your-username/titanic-baseline
```

Status: `QUEUED` → `RUNNING` → `COMPLETE` or `ERROR`

## Real-world example: March Machine Learning Mania 2026

Here is an example using this tool for the [March Machine Learning Mania 2026](https://www.kaggle.com/competitions/march-machine-learning-mania-2026) competition (NCAA tournament prediction).

```bash
# Create the competition directory with GPU enabled
kaggle-notebook-deploy init march-machine-learning-mania-2026 --gpu --public

# Edit the notebook
vim march-machine-learning-mania-2026/march-machine-learning-mania-2026-baseline.ipynb

# Validate → Deploy
kaggle-notebook-deploy validate march-machine-learning-mania-2026
kaggle-notebook-deploy push march-machine-learning-mania-2026
```

## Common Pitfalls

### 1. `enable_internet: false` is required for code competitions

In code competitions, internet access is disabled in submitted notebooks. If `enable_internet: true`, the Submit button is grayed out.

`kaggle-notebook-deploy init` sets this to `false` by default, so you're safe as long as you don't use the `--internet` flag.

### 2. Data path gotcha

| Source type | `kernel-metadata.json` key | Mount path |
|---|---|---|
| Competition data | `competition_sources` | `/kaggle/input/competitions/<slug>/` |
| Dataset | `dataset_sources` | `/kaggle/input/<slug>/` |

**`competition_sources` includes a `competitions/` subdirectory.** This is a common source of confusion.

To debug paths inside a notebook:

```python
from pathlib import Path
for item in sorted(Path('/kaggle/input').iterdir()):
    print(f'  {item.name}/')
    for sub in sorted(item.iterdir()):
        print(f'    {sub.name} ({sub.stat().st_size:,} bytes)')
```

### 3. API-based submit is not available

The Kaggle `CreateCodeSubmission` API returns 403 with a public token due to insufficient permissions (as of Feb 2026).

**The final Submit requires browser interaction.** This is a Kaggle limitation, outside the scope of kaggle-notebook-deploy.

### 4. `kaggle kernels push` resets Secrets

Kaggle Notebook "Secrets" (e.g., W&B API keys) are unlinked each time you run `kaggle kernels push`.

**Workaround**: Push via CLI → Re-enable Secrets in the browser Web UI → Run

### 5. Accept competition rules first

To mount competition data via `competition_sources`, you must accept the competition rules in the browser. If you haven't accepted them, the data won't be mounted and you'll get a `FileNotFoundError`.

## Recommended directory structure

```
my-kaggle/
├── .github/workflows/
│   └── kaggle-push.yml                      # generated by init-repo
├── scripts/
│   └── setup-credentials.sh                 # generated by init-repo
├── titanic/                                  # generated by init titanic
│   ├── kernel-metadata.json
│   └── titanic-baseline.ipynb
├── house-prices/                             # generated by init house-prices
│   ├── kernel-metadata.json
│   └── house-prices-baseline.ipynb
├── .gitignore
└── README.md
```

One directory per competition, each with its own `kernel-metadata.json` and notebook. A single GitHub Actions workflow handles all competitions via the `notebook_dir` parameter.

## Command reference

### `kaggle-notebook-deploy init <competition-slug>`

Generate a competition directory from a template.

| Option | Description | Default |
|---|---|---|
| `-u, --username` | Kaggle username | read from `~/.kaggle/kaggle.json` |
| `-t, --title` | Notebook title | auto-generated from slug |
| `--gpu` | Enable GPU | off |
| `--internet` | Enable internet | off (recommended for code competitions) |
| `--public` | Public notebook | off (private) |

### `kaggle-notebook-deploy init-repo`

Set up GitHub Actions workflow in the repository.

| Option | Description |
|---|---|
| `-f, --force` | Overwrite existing files |

### `kaggle-notebook-deploy validate [directory]`

Validate `kernel-metadata.json`. Exits with code 1 on error.

### `kaggle-notebook-deploy push [directory]`

Push notebook to Kaggle (runs `kaggle kernels push` internally).

| Option | Description |
|---|---|
| `--skip-validate` | Skip validation |
| `--dry-run` | Print command without executing |

## Why can't it be fully automated?

The ideal would be for `git push` alone to complete the entire submission, but Kaggle-side limitations prevent it:

1. **API restriction**: `CreateCodeSubmission` API returns 403 with a public token
2. **Secrets reset**: `kaggle kernels push` unlinks Secrets bindings
3. **Rule acceptance**: Competition participation requires browser-based acceptance

Even so, **automating code management, diff review, and deployment** already dramatically improves the development experience.

## Summary

```bash
pip install kaggle-notebook-deploy           # install
kaggle-notebook-deploy init-repo             # set up repository
kaggle-notebook-deploy init titanic          # join a competition
# ... edit the notebook ...
kaggle-notebook-deploy push titanic          # deploy
```

Bring the full GitHub ecosystem — version control, Actions, Secrets, Pull Requests — to your Kaggle competitions. Say goodbye to the browser editor.

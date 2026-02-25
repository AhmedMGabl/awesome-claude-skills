---
name: python-poetry
description: Python Poetry patterns covering dependency management, virtual environments, pyproject.toml, version constraints, publishing, monorepos, and CI/CD integration.
---

# Python Poetry

This skill should be used when managing Python projects with Poetry. It covers dependency management, virtual environments, pyproject.toml, publishing, and CI/CD.

## When to Use This Skill

Use this skill when you need to:

- Manage Python dependencies with Poetry
- Configure pyproject.toml for projects
- Handle virtual environments and lockfiles
- Publish packages to PyPI
- Integrate Poetry in CI/CD pipelines

## Setup

```bash
curl -sSL https://install.python-poetry.org | python3 -
# or
pip install poetry
```

## Create New Project

```bash
poetry new my-project
# Creates:
# my-project/
# ├── pyproject.toml
# ├── README.md
# ├── my_project/
# │   └── __init__.py
# └── tests/
#     └── __init__.py

# Or initialize in existing directory
cd existing-project
poetry init
```

## pyproject.toml

```toml
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = "A sample project"
authors = ["Alice <alice@example.com>"]
readme = "README.md"
packages = [{include = "my_project"}]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.110"
sqlalchemy = "^2.0"
pydantic = "^2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
pytest-cov = "^4.0"
ruff = "^0.3"
mypy = "^1.0"

[tool.poetry.group.docs.dependencies]
mkdocs = "^1.5"

[tool.poetry.scripts]
myctl = "my_project.cli:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## Dependency Management

```bash
# Add dependencies
poetry add fastapi uvicorn sqlalchemy
poetry add "pydantic>=2.0,<3.0"

# Add dev dependencies
poetry add --group dev pytest ruff mypy

# Add optional group
poetry add --group docs mkdocs

# Remove dependencies
poetry remove sqlalchemy

# Update dependencies
poetry update                  # all
poetry update fastapi          # specific

# Show dependency tree
poetry show --tree
poetry show --outdated
```

## Version Constraints

```toml
# Caret (^): allow patch and minor updates
fastapi = "^0.110"    # >=0.110.0, <0.111.0 (for 0.x)
pydantic = "^2.0"     # >=2.0.0, <3.0.0

# Tilde (~): allow patch updates only
requests = "~2.31"    # >=2.31.0, <2.32.0

# Exact
uvicorn = "0.27.1"

# Wildcard
pytest = "8.*"         # >=8.0.0, <9.0.0

# Range
sqlalchemy = ">=2.0,<3.0"
```

## Virtual Environments

```bash
# Create/activate venv
poetry install              # install all deps + create venv
poetry shell                # activate venv
poetry env info             # show venv info
poetry env list             # list venvs

# Run commands in venv
poetry run python main.py
poetry run pytest
poetry run myctl --help

# Configure venv location
poetry config virtualenvs.in-project true  # .venv in project dir
```

## Lock File

```bash
# Generate/update lock file
poetry lock

# Install from lock file (exact versions)
poetry install

# Install without dev dependencies
poetry install --without dev

# Install specific groups
poetry install --with docs
```

## Building and Publishing

```bash
# Build package
poetry build
# Creates dist/my_project-0.1.0.tar.gz
# Creates dist/my_project-0.1.0-py3-none-any.whl

# Publish to PyPI
poetry publish

# Publish to private registry
poetry config repositories.private https://pypi.mycompany.com/simple/
poetry publish -r private

# Version bumping
poetry version patch    # 0.1.0 -> 0.1.1
poetry version minor    # 0.1.1 -> 0.2.0
poetry version major    # 0.2.0 -> 1.0.0
```

## CI/CD Integration

```yaml
# GitHub Actions
- name: Install Poetry
  uses: snok/install-poetry@v1
  with:
    version: latest
    virtualenvs-create: true
    virtualenvs-in-project: true

- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: .venv
    key: venv-${{ hashFiles('**/poetry.lock') }}

- name: Install dependencies
  run: poetry install --no-interaction

- name: Run tests
  run: poetry run pytest --cov
```

## Tool Configuration

```toml
# pyproject.toml - tool configs alongside Poetry

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=my_project"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
strict = true
python_version = "3.11"
```

## Additional Resources

- Poetry: https://python-poetry.org/
- Docs: https://python-poetry.org/docs/
- CLI Reference: https://python-poetry.org/docs/cli/

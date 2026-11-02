(installation)=

# Installation

E2x Course Hub can be installed from PyPI via:

```bash
pip install e2x-course-hub
```

To install the latest development version from GitHub instead:

```bash
pip install git+https://github.com/Digiklausur/e2x-course-hub
```

Installing from source builds `course-service-ui` (the bundled React frontend) via
`hatch-jupyter-builder` and bundles the result into the wheel, so a working `npm` must
be on `PATH`.

## For development

```bash
git clone https://github.com/Digiklausur/e2x-course-hub
cd e2x-course-hub
pip install -e ".[dev]"
```

This also installs `ruff` for linting. See the
[project README](https://github.com/Digiklausur/e2x-course-hub#development) for
frontend-only development commands (`npm run dev`, linting, etc.).
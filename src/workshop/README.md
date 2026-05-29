# workshop package

This folder is the intended active Python package path for Local Agent Workshop.

The intended CLI entrypoint is:

```toml
[project.scripts]
workshop = "workshop.cli:main"
```

If connector safety filters prevent creating Python package files here, create these files locally or through Codex:

```text
src/workshop/__init__.py
src/workshop/cli.py
```

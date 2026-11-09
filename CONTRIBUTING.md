# Contributing

English and Chinese issues and pull requests are welcome.

For bugs, provide a minimal Markdown example, expected behavior, actual behavior, OS, Python version, and dependency version. Replace private data with synthetic values. Discuss major format or dependency changes in an issue before implementing them.

## Local checks

Use Python 3.10+ in a virtual environment:

```bash
python -m pip install -r skills/project-report/requirements.txt PyYAML
python skills/project-report/scripts/test_render_report.py
python scripts/validate_package.py
python skills/project-report/scripts/render_report.py skills/project-report/assets/example.md
```

For visual changes, inspect the generated HTML at desktop and narrow widths. Include before/after screenshots in the PR. Keep chart values derived from Markdown tables, preserve existing report content, and add behavioral tests for changes to parsing, numeric handling, output safety, or data synchronization.

Keep generated caches, local virtual environments, credentials, personal paths, and private reports out of commits. Update the format reference when changing syntax. Update the public demo and preview when the appearance changes; only use synthetic or explicitly licensed public data.

PRs should explain the problem, the behavior change, validation, and any compatibility impact. By submitting a contribution, you agree that it may be distributed under this project's MIT license. Follow the [Code of Conduct](CODE_OF_CONDUCT.md). Report vulnerabilities according to [SECURITY.md](SECURITY.md).

# Contributing to RUNE

Thank you for your interest in contributing! RUNE is an early-stage but fast-moving project. Here’s how to get started.

---

## 🔧 Project Setup

1. **Fork the repo** and clone it locally:

   ```bash
   git clone https://github.com/<your-username>/rune.git
   cd rune
   ```

2. **Set up a virtualenv**:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```

3. **Run CLI locally**:

   ```bash
   python rune_cli.py run noop --node testhost
   ```

---

## ✍️ Contributing a Plugin

1. Create a Bash script in `plugins/`
2. Follow the [Plugin Development Guide](plugin_development_guide.md)
3. Test it with example JSON piped into stdin
4. Make sure it returns structured JSON and exits correctly

---

## 🧪 Running Tests

```bash
pytest tests/
```

Add tests for any new modules you create under `rune/` or `plugins/`.

---

## 🔁 Pull Request Process

- Fork → Feature branch → PR
- Reference an issue (or create one)
- Ensure all tests pass and no linting errors
- Document any changes in `docs/`

---

## 🙏 Community Standards

Be respectful. No drama. Fix bugs. Write useful things.

---

## 🔍 Where to Help

- Plugin development
- CLI enhancements
- SSM transport fallback
- Plugin registry/metadata logic
- Docs, tests, diagrams

Thanks for improving RUNE!

© 2025 Richard Majewski. Licensed under the MPL-2.0.

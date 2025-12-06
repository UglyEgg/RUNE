# RUNE Testing Guide

This guide describes how to validate RUNE core logic, plugin behavior, and overall integration using structured tests.

---

## 🔍 Types of Tests

### Unit Tests

Located in `tests/`

- Test `rune_cli.py`, `orchestrator.py`, `mediator.py`
- Use mocks for SSH/SSM transport to avoid real remote execution

### Plugin Tests

- Pipe mock input JSON into each plugin
- Capture and validate structured JSON output
- Ensure correct exit codes and error handling

### Integration Tests

- Simulate end-to-end execution:

  ```bash
  rune run restart-docker --node testhost --dry-run
  ```

- Verify orchestration, payload formatting, transport call, and output parsing

---

## 🧪 Plugin Testing Example

```bash
echo '{
  "payload": { "data": { "input_parameters": {} } }
}' | ./plugins/restart-docker.sh | jq .
```

- Output must be valid JSON
- Exit code `0` for success
- Exit `1+` for failure with proper `error` key

---

## ✅ Test Checklist

- [ ] All core modules have unit test coverage ≥ 80%
- [ ] Every plugin has a test case and error case
- [ ] Transport fallbacks (mocked)
- [ ] CLI flags are respected in tests

---

## Tools

- `pytest`
- `unittest.mock`
- `jq` (for CLI-level JSON parsing)
- GitHub Actions (CI-ready)

---

Stay strict. RUNE actions must always behave predictably, or not at all.

© 2025 Richard Majewski. Licensed under the MPL-2.0.

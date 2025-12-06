# **Advanced Admin Guide: Direct JSON Construction with `rune_ok` / `rune_error`**

This guide is for experienced Bash users who want **full control** over the JSON returned to RUNE. Instead of using the beginner-friendly accumulator functions (`rune_out`, `rune_err`, `rune_finish`), you will:

- Write JSON manually using **jq -n**

- Pass it directly to `rune_ok` or `rune_error`

- Build nested structures, arrays, complex types, etc.

This method provides the most power and flexibility.

---

# 🚀 **1. When You Should Use This Method**

Use direct JSON construction when:

- You need nested objects or arrays (not just flat key=value)

- Fields require type correctness (numbers, booleans, nulls)

- Your output must follow a specific schema

- The fix‑it script produces complex diagnostics

- You need full control of error formatting

If your script is simple, the beginner approach is recommended.

---

# ⚠️ **2. Direct JSON Output Pattern**

You are responsible for building `output_data` or `error.data`.

### Example JSON construction via jq:

```bash
OUTPUT=$(jq -n \
  --arg service "$SERVICE" \
  --argjson attempts "$ATTEMPTS" \
  '{service: $service, attempts: $attempts}')
```

Then pass it to RUNE:

```bash
rune_ok "Service restarted" "$OUTPUT"
```

### Or on error:

```bash
ERRDATA=$(jq -n --arg reason "$REASON" '{reason: $reason}')
rune_error 2001 "Restart failed" "$ERRDATA"
```

---

# 🧠 **3. Pros & Cons of the Advanced JSON Method**

## ✅ **Pros** (Why senior admins prefer it)

- Full control of JSON structure

- Supports nested objects / arrays

- Strong typing: numbers, booleans, null

- Output can match external schemas

- Most flexible for automation, reporting, observability

## ❌ **Cons**

- Requires jq knowledge

- Slightly more verbose

- More opportunities for syntax errors

- Must ensure JSON is valid

---

# 📘 **4. Direct Access to All Metadata and Parameters**

You can use:

```bash
rune_param "key" "default"
rune_param_json "key" "{}"
rune_meta "key" "default"
```

But now you also have the option to embed data *directly into JSON*.

### Example:

```bash
NODE=$(rune_meta "node" "unknown")
PARAMS=$(rune_all_params)   # raw JSON map
```

Embed these directly:

```bash
OUTPUT=$(jq -n \
  --arg node "$NODE" \
  --argjson params "$PARAMS" \
  '{node: $node, parameters: $params}')
```

---

# 🛠️ **5. Example: Service Restart with Structured Output**

```bash
#!/usr/bin/env bash
set -euo pipefail
. /opt/rune/lib/rune_bpcs.sh
rune_init

SERVICE=$(rune_param "service" "nginx")
ATTEMPTS=$(rune_param "attempts" "1")

NODE=$(rune_meta "node" "unknown")

attempt_counter=0
success=false

while (( attempt_counter < ATTEMPTS )); do
    if systemctl restart "$SERVICE"; then
        success=true
        break
    fi
    attempt_counter=$((attempt_counter + 1))
done

if [[ "$success" == true ]]; then
    OUTPUT=$(jq -n \
      --arg service "$SERVICE" \
      --argjson attempts "$ATTEMPTS" \
      --arg node "$NODE" \
      '{service: $service, attempts: $attempts, node: $node, restarted: true}')
    rune_ok "Service restarted successfully" "$OUTPUT"
else
    ERRDATA=$(jq -n \
      --arg service "$SERVICE" \
      --argjson attempts "$ATTEMPTS" \
      --arg node "$NODE" \
      '{service: $service, attempts: $attempts, node: $node, restarted: false}')
    rune_error 2100 "Service restart failed" "$ERRDATA"
fi
```

---

# 🧰 **6. Example: Returning a Nested JSON Structure**

```bash
ROOT=$(mktemp -d)
tar -czf "$ROOT/archive.tar.gz" /var/log

OUTPUT=$(jq -n \
  --arg path "$ROOT/archive.tar.gz" \
  --argjson stats '{lines:1204, size_mb:12.4}' \
  '{artifact: {path: $path, stats: $stats}, status: "ok"}')

rune_ok "archive complete" "$OUTPUT"
```

This creates:

```json
{
  "artifact": {
    "path": "/tmp/archive.tar.gz",
    "stats": {"lines":1204,"size_mb":12.4}
  },
  "status": "ok"
}
```

---

# 🛡️ **7. Best Practices for Senior Scripters**

### ✔ Use jq for **all** JSON creation

Never hardcode JSON with echo.

### ✔ Validate complex JSON during development

```bash
echo "$OUTPUT" | jq .
```

### ✔ Keep output small and meaningful

Too much data slows transfer.

### ✔ Always supply numeric fields using `--argjson`

```bash
--argjson count "$COUNT"
```

### ✔ Use snake_case keys for consistency

Example: `artifact_path`, `disk_usage`, `restart_attempts`.

### ✔ Prefer structured objects over unstructured strings

Good:

```json
{"stats": {"lines": 120, "errors": 2}}
```

Not good:

```json
{"stats": "120 lines, 2 errors"}
```

---

# 🧩 **8. Combining Advanced and Beginner Methods (Hybrid Mode)**

You *can* mix:

- `rune_out` for simple fields

- manual JSON for complex structures

- `rune_finish` to finalize

But if you’re building advanced JSON, it’s cleaner to:

- Stick entirely to `rune_ok` / `rune_error`

- Build one clean output payload

---

# 🎓 **9. Summary**

This advanced method gives you:

- Precision

- Structure

- Strong typing

- Flexibility

Use it when creating:

- Diagnostic tools

- Report generators

- Nested or typed data outputs

- Anything that requires more than simple key/values

If your script is simple, choose the beginner version for speed and clarity.

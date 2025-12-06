# **Beginner Admin Guide: Writing Fix‑It Scripts with `rune_out`, `rune_err`, and `rune_finish`**

This guide is written for newer or occasional Bash scripters who need to write **fix‑it scripts** for RUNE. You **do not** need to know JSON, jq, or advanced Bash. The shared library (`rune_bpcs.sh`) handles everything for you.

Your job is simply to:

1. Read inputs using `rune_param` / `rune_meta`

2. Add return values using `rune_out`

3. Report failures using `rune_err`

4. End the script using `rune_finish`

That’s it!

---

# ✅ **1. Required Script Template**

Every fix‑it plugin should start like this:

```bash
#!/usr/bin/env bash
set -euo pipefail

. /opt/rune/lib/rune_bpcs.sh
rune_init
```

And end like this:

```bash
rune_finish "optional success message"
```

Everything else happens between those lines.

---

# ✅ **2. Reading Inputs**

Inputs come from RUNE as parameters.

```bash
VALUE=$(rune_param "name_of_param" "default_value")
```

Examples:

```bash
SERVICE=$(rune_param "service" "nginx")
FORCE=$(rune_param "force" "false")
```

Metadata (like which node you’re on):

```bash
NODE=$(rune_meta "node" "unknown")
```

---

# ✅ **3. Returning Output Values**

Instead of printing text, you send structured data using:

```bash
rune_out key value
```

Examples:

```bash
rune_out service "$SERVICE"
rune_out restarted "true"
rune_out log_path "/tmp/logs.tar.gz"
```

These values become part of the JSON RUNE receives — but **you never have to write JSON**.

---

# ❌ **4. Reporting Errors (Don’t exit manually!)**

If something fails:

```bash
rune_err 2001 "Failed to restart service"
```

You can still add additional fields:

```bash
rune_out service "$SERVICE"
rune_err 2002 "Permission denied restarting service"
```

RUNE will treat the script as failed after `rune_finish` is called.

---

# ✅ **5. Finalizing Execution**

Your script must call:

```bash
rune_finish
```

This outputs the final JSON response and exits with the right code.

If you want to include a custom success message:

```bash
rune_finish "cleanup complete"
```

---

# ⭐ **6. Beginner Example #1: Restart a Service**

```bash
#!/usr/bin/env bash
set -euo pipefail
. /opt/rune/lib/rune_bpcs.sh
rune_init

SERVICE=$(rune_param "service" "nginx")
NODE=$(rune_meta "node" "unknown")

echo "Restarting $SERVICE on $NODE" >&2

if systemctl restart "$SERVICE"; then
    rune_out service "$SERVICE"
    rune_out restarted "true"
else
    rune_out service "$SERVICE"
    rune_out restarted "false"
    rune_err 2001 "Failed to restart service"
fi

rune_finish "service restart"
```

---

# ⭐ **7. Beginner Example #2: Collect Logs**

```bash
#!/usr/bin/env bash
set -euo pipefail
. /opt/rune/lib/rune_bpcs.sh
rune_init

WORKDIR=$(mktemp -d)
TARFILE=$(mktemp /tmp/logs-XXXXXX.tar.gz)

cp /var/log/syslog "$WORKDIR"/syslog 2>/dev/null || true
cp /var/log/messages "$WORKDIR"/messages 2>/dev/null || true

tar -czf "$TARFILE" -C "$WORKDIR" .

rune_out artifact_path "$TARFILE"
rune_out message "logs collected"
rune_finish
```

---

# ⚖️ **8. Pros & Cons of the Beginner Method**

### **Pros**

- No JSON required — library builds everything

- Very easy to learn

- Hard to break

- Cleaner, shorter scripts

### **Cons**

- Less control over JSON structure

- Output values are all stored as flat key/value pairs

- Cannot create nested JSON objects

---

# 🎯 **9. When to Use This Method**

Use the beginner API when you want:

- Fast development

- Simple fix‑it scripts

- A low chance of formatting mistakes

- Clarity and consistency

If you need **custom JSON**, switch to the mid/senior guide.

---

# 🎉 **You’re Ready to Write Plugins!**

With just `rune_out`, `rune_err`, and `rune_finish`, you can write reliable RUNE fix‑it scripts without ever touching JSON.

If you’d like an even shorter cheat sheet, I can generate one too.

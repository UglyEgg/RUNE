# **RUNE BPCS Library — API Reference**

This document describes every function provided by `rune_bpcs.sh`, including inputs, outputs, behavior, and usage notes. This serves as the authoritative API reference for script authors.

---

# **Table of Contents**

1. Initialization
   
   - `rune_init`

2. Parameter Functions
   
   - `rune_param`
   
   - `rune_param_json`
   
   - `rune_all_params`

3. Metadata Functions
   
   - `rune_meta`

4. Core Output Functions
   
   - `rune_ok`
   
   - `rune_error`

5. Accumulator Output System
   
   - `rune_out`
   
   - `rune_err`
   
   - `rune_finish`

6. Convenience Functions
   
   - `rune_ok_kv`
   
   - `rune_error_kv`

---

# 🔧 **1. Initialization**

## `rune_init`

### **Purpose:**

Reads JSON from stdin, parses core sections, populates internal state for parameter and metadata access.

### **Signature:**

```bash
rune_init
```

### **Behavior:**

- Must be called **exactly once**, near the top of every plugin.

- Parses:
  
  - `message_metadata`
  
  - `observability`
  
  - `routing`
  
  - `payload.data.input_parameters`

- Fails if no input is provided.

- Requires `jq` to be installed.

### **Returns:**

Nothing. Initializes global variables.

---

# 🔡 **2. Parameter Functions**

## `rune_param`

### **Purpose:**

Retrieve a string parameter from `input_parameters` with a fallback default.

### **Signature:**

```bash
value=$(rune_param "key" "default")
```

### **Inputs:**

- `key` — parameter name.

- `default` — value returned if key is missing.

### **Output:**

A string. Boolean and numeric JSON values are converted to their string equivalents.

---

## `rune_param_json`

### **Purpose:**

Retrieve a parameter *as raw JSON*.

### **Signature:**

```bash
json_value=$(rune_param_json "key" "{}")
```

### **Inputs:**

- `key` — parameter name.

- `default_json` — valid JSON value used if missing.

### **Output:**

A JSON string (compact format).

### **Use case:**

- Arrays: `extra_paths=["/var/log/syslog", "/tmp/test.log"]`

- Nested objects

---

## `rune_all_params`

### **Purpose:**

Return the entire `input_parameters` structure as JSON.

### **Signature:**

```bash
params=$(rune_all_params)
```

### **Output:**

A JSON object.

---

# 🗂️ **3. Metadata Functions**

## `rune_meta`

### **Purpose:**

Retrieve a value from the `message_metadata` block.

### **Signature:**

```bash
value=$(rune_meta "key" "default")
```

### **Typical metadata keys:**

- `node`

- `action`

- `trace_id`

- `request_id`

### **Output:**

String.

---

# 📤 **4. Core Output Functions**

These functions print a full JSON response to stdout and exit.

---

## `rune_ok`

### **Purpose:**

Send a success response to RUNE.

### **Signature:**

```bash
rune_ok "message" "output_json"
```

### **Inputs:**

- `message` — short textual summary

- `output_json` — JSON object containing results

### **Behavior:**

- Prints a JSON structure containing:
  
  - metadata
  
  - observability
  
  - routing
  
  - payload.result = "success"
  
  - payload.output_data = provided JSON

- Exits with code **0**.

---

## `rune_error`

### **Purpose:**

Send an error response to RUNE.

### **Signature:**

```bash
rune_error CODE "message" "error_data_json"
```

### **Inputs:**

- `CODE` — exit code (non‑zero)

- `message` — error summary

- `error_data_json` — JSON object describing error context

### **Behavior:**

- Prints a JSON structure containing:
  
  - metadata
  
  - observability
  
  - routing
  
  - payload.result = "error"
  
  - payload.output_data = {…}
  
  - error.code
  
  - error.message
  
  - error.data

- Exits with code `CODE`.

---

# 📦 **5. Accumulator Output System**

These functions allow script authors to output key/value pairs without building JSON.

---

## `rune_out`

### **Purpose:**

Record a key/value pair to be included in final output.

### **Signature:**

```bash
rune_out KEY VALUE
# or
rune_out "KEY=VALUE"
```

### **Inputs:**

- `KEY VALUE` — recommended form

- `"KEY=VALUE"` — alternative

### **Behavior:**

Stores fields internally until `rune_finish` is called.

### **Output:**

None.

---

## `rune_err`

### **Purpose:**

Record that an error has occurred.

### **Signature:**

```bash
rune_err CODE "message"
```

### **Inputs:**

- `CODE` — numeric error code

- `message` — description

### **Behavior:**

Marks script as failed; does **not** exit immediately.

---

## `rune_finish`

### **Purpose:**

Finalize execution based on accumulated output.

### **Signature:**

```bash
rune_finish
rune_finish "success message"
```

### **Behavior:**

- Builds JSON:
  
  - If `rune_err` was called → calls `rune_error`
  
  - Otherwise → calls `rune_ok`

- Uses all accumulated `rune_out` fields

- Exits automatically

### **Output:**

Structured JSON for RUNE.

---

# 🧰 **6. Convenience Wrappers**

## `rune_ok_kv`

### **Purpose:**

Send a success result using simple `key=value` pairs.

### **Signature:**

```bash
rune_ok_kv "message" \
  "key1=value1" \
  "key2=value2"
```

### **Behavior:**

- Converts pairs into a JSON object

- Calls `rune_ok`

---

## `rune_error_kv`

### **Purpose:**

Send an error result using simple `key=value` pairs.

### **Signature:**

```bash
rune_error_kv CODE "message" \
  "key1=value1" \
  "key2=value2"
```

### **Behavior:**

- Converts pairs into `error.data`

- Calls `rune_error`

---

# 🏁 **End of API Reference**

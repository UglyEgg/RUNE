# Diagrams

This page consolidates key diagrams used throughout the documentation. Individual pages link here to avoid repeating diagrams.

## System context

```mermaid
flowchart LR
  O[Operator / Automation] --> CLI[CLI]
  CLI --> LOM[LOM Orchestrator]
  LOM --> LMM[LMM Mediator]
  LMM -->|SSH/SSM| HOST[Remote Host]
  HOST --> PLUG[Plugin Script]
  PLUG --> HOST --> LMM --> LOM --> CLI
```

## Positioning in the automation stack

```mermaid
flowchart TB
  A[Signals & Triggers<br/>Monitoring • SIEM • SOAR • ITSM • On-call] --> B[RUNE<br/>Mediated remediation orchestration]

  B --> C[Action Plugins<br/>Bash/Python • strict I/O]
  B --> D[CM / Automation Tools<br/>Ansible • Salt • Puppet • Chef<br/>Terraform adjacent]

  C --> E[Execution Transport<br/>SSH • AWS SSM]
  E --> F[Targets<br/>Linux hosts • instances • customer-managed envs]

  D -. optional invocation .-> E
```

## Runtime execution sequence

```mermaid
sequenceDiagram
  participant CLI
  participant LOM
  participant LMM
  participant HOST as Remote Host
  participant PLUG as Plugin

  CLI->>LOM: RCS execute_action
  LOM->>LMM: RCS route/validate
  LMM->>HOST: SSH/SSM run plugin
  HOST->>PLUG: BPCS stdin JSON
  PLUG-->>HOST: BPCS stdout JSON + exit code
  HOST-->>LMM: stdout/stderr/exit
  LMM-->>LOM: RCS response (result) or EPS
  LOM-->>CLI: CLI JSON output
```

## Module registration flow

```mermaid
flowchart LR
  MOD[Module / Plugin] -->|MRS register| LOM[LOM Registry Owner]
  LOM -->|registry snapshot/query| LMM[LMM Router]
  LMM -->|route decision| EXEC[Execution Path]
```

## Error handling flow

```mermaid
flowchart TB
  R[RCS request received] --> V[Validate request]
  V --> X[Execute via LMM]
  X --> P[Parse plugin output]
  P -->|ok + exit=0| S[RCS success response]
  P -->|invalid JSON or exit!=0| M[Map to EPS]
  M --> H[Route EPS to ErrorHandler]
  H --> E[RCS error response]
```

## Mediation boundary

```mermaid
flowchart LR
  subgraph "RUNE"
    CLI[CLI] --> LOM[LOM]
    LOM --> LMM[LMM]
    A[Module A] --> LMM
    B[Module B] --> LMM
    ERR[ErrorHandler] --> LMM
  end

  A -. "no direct module-to-module" .- B
```

## Policy gates

```mermaid
flowchart TB
  IN[RCS request] --> VAL[Validate schema + routing]
  VAL -->|reject| EPS[Emit EPS]
  VAL --> POL[Policy gates<br/>allowlist • rate limit • safeguards]
  POL -->|reject| EPS
  POL --> MODE[Select mode<br/>local or remote]
  MODE --> RUN[Invoke plugin]
  RUN --> OUT[Validate plugin output]
  OUT -->|success| OK[RCS result]
  OUT -->|failure| EPS
```

## Plugin lifecycle

```mermaid
stateDiagram-v2
  [*] --> Discovered
  Discovered --> Validated
  Validated --> Runnable
  Runnable --> Executing
  Executing --> Succeeded: exit=0 + valid JSON
  Executing --> Failed: exit!=0 or invalid JSON
  Failed --> Quarantined: repeated failure (optional)
  Quarantined --> Runnable: manual restore (optional)
```

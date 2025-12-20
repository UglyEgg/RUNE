# Security model

RUNE is designed for corporate IT environments where remote remediation is powerful and therefore risky. The security model is built around separation of concerns and explicit trust boundaries.

RUNE assumes you already have an authenticated and authorized transport. RUNE does not invent a new remote access system. It uses established mechanisms (SSH or SSM) and focuses on safe execution, observability, and consistent outcomes.

## Trust boundaries

### Operator boundary

The CLI is an operator interface. Your organization controls:

- who is allowed to run RUNE
- which actions they can execute
- how approvals are handled (change management, break glass)

### Mediation boundary

The LMM is the enforcement point. It is responsible for:

- transport selection and configuration
- output validation and normalization
- consistent error handling and routing
- applying timeouts and retry policy

Plugins never bypass mediation.

### Target node boundary

Plugins execute on the target node with the privileges available to the transport user.

This is deliberate. In most corporate environments, privilege is managed via:

- sudo policies
- SSM command execution policies
- OS level access controls

RUNE does not replace those systems.

## Threat model highlights

### Risk: arbitrary command execution

RUNE executes scripts on remote nodes. This is inherently high impact.

Mitigations:

- controlled plugin distribution (package repo, signed artifacts, change control)
- narrow plugin scope and least privilege sudo rules
- registry driven allow lists and policy enforcement in LOM
- explicit high impact action flags that require operator acknowledgment

### Risk: untrusted plugin output

Plugins are treated as untrusted input. The LMM:

- requires one JSON object on stdout
- captures stderr separately
- validates the BPCS structure before trusting any fields
- normalizes failures into EPS for consistent handling

### Risk: secrets exposure

Plugins should not print secrets. RUNE supports structured output, so you can:

- avoid dumping configuration files
- return only required values
- keep verbose diagnostics in stderr and restrict log collection

Operationally, handle secrets via:

- environment injection from your secret manager
- SSM parameters or secure files on node
- minimal output policies in your log pipeline

### Risk: replay and tampering (future capable)

RCS and EPS include optional security metadata fields (identity, signatures, key ids). These exist so deployments can add message signing or encryption where needed, without changing the envelope shape.

If you do not implement signing, do not rely on these fields for security. Rely on the transport security and operational controls.

## Audit and observability

RUNE is designed to be auditable:

- message id and correlation id provide request lineage
- trace id and span id support cross system correlation
- errors are normalized into EPS with fingerprints and context

This makes it practical to feed RUNE outputs into SIEM and incident management systems.

## Recommended operational practices

- treat plugin bundles as production artifacts with review and versioning
- run RUNE from controlled runners (CI, automation hosts) rather than laptops where possible
- keep actions small, idempotent when feasible, and explicitly reversible when not
- log structured results centrally and restrict raw stderr logs as needed

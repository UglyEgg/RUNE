# Roadmap

This roadmap focuses on capabilities that matter in corporate IT operations: safety, observability, controlled extensibility, and predictable execution.

RUNE is protocol first. The protocol contracts (RCS, MRS, BPCS, EPS) are stable foundations. Features build on top without breaking those contracts.

## Phase 0: Contract alignment

- RCS, MRS, BPCS, EPS published and treated as canonical
- LOM and LMM implement mediation and registry behaviors
- CLI provides deterministic action execution and JSON output

## Phase 1: Transport hardening

- SSH transport improvements (timeouts, retries, concurrency control)
- SSM transport support where available
- node identity and inventory integration hooks

## Phase 2: Registry and discovery

- action catalog generation from plugin bundles
- operator friendly action listing and description
- per action policy metadata (timeouts, approvals, risk flags)

## Phase 3: Observability and audit

- structured logs suitable for SIEM ingestion
- trace propagation and correlation improvements
- EPS fingerprint and error taxonomy stabilization

## Phase 4: Packaging and distribution

- plugin bundle packaging patterns (RPM/DEB or internal artifact pipelines)
- version compatibility story between CLI, core, and plugin bundles
- signed artifact support in controlled environments

## Phase 5: Workflow features

- optional action chaining driven by explicit policy
- guardrails for high impact sequences
- richer rollback and compensating action modeling

## Non goals

- RUNE is not a full configuration management or state enforcement platform
- RUNE does not aim to replace SSH, SSM, or existing access control systems

For implementation priorities, align roadmap work with real operational needs: what your on call engineers actually do under pressure.

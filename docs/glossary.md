# Glossary

**Action**  
A named capability that RUNE can execute on a node. In practice, an action maps to a plugin executable plus metadata in the registry.

**BPCS**  
Bash Plugin Communication Specification. Defines the JSON contract for plugin stdin and stdout.

**CLI**  
Command line interface used by operators and automation to request actions.

**EPS**  
Error Protocol Specification. Defines the structured error envelope used by RUNE for failures that must propagate through the system.

**LOM**  
Lifecycle Orchestration Module. Validates requests, applies policy, and owns registry and lifecycle.

**LMM**  
Local Mediation Module. Routes and executes requests, selects transports, validates outputs, and normalizes errors.

**Module**  
A logical component that provides a capability and communicates using RCS. Examples include LOM, LMM, ErrorHandler, and plugin capability providers.

**MRS**  
Module Registration Specification. Defines how modules declare identity, capabilities, and operational metadata.

**Node**  
A target system where an action runs. Typically a Linux host reachable by SSH or managed by SSM.

**Plugin**  
An executable on the target node that implements an action. For Bash plugins, the plugin speaks BPCS and should use the shared library.

**RCS**  
Runtime Communication Specification. Defines the runtime message envelope used between modules and for request correlation.

**Transport**  
A mechanism used to execute plugins on a node, such as SSH or AWS SSM.

**Trace**  
Identifiers (`trace_id`, `span_id`, correlation id) carried through messages to support observability and audit.

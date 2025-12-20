# Documentation map

This page is the navigation and reading guide for RUNE. It is intentionally light on repeated explanations so the documentation stays consistent over time.

## Recommended reading paths

### If you want the 2 minute overview

1. [Why RUNE](why_rune.md)
2. [Architecture](architecture.md)
3. [Quick start](quick_start.md)

### If you want to understand how execution is controlled

1. [Mediation model](mediation_model.md)
2. [Action lifecycle](lifecycle.md)
3. [Security model](security_model.md)

### If you want to understand the protocol contracts

- [Runtime Communication Specification (RCS)](rcs.md)
- [Module Registration Specification (MRS)](mrs.md)
- [Bash Plugin Communication Specification (BPCS)](bpcs.md)
- [Error Protocol Specification (EPS)](eps.md)
- [JSON appendix](json_appendix.md)

### If you want to build plugins

1. [Plugin development guide](plugin_dev_guide.md)
2. [Bash library reference](bash_library_reference.md)
3. [Testing guide](testing.md)

## What each section is for

### Concepts

The high level model of how RUNE works, what problems it is designed to solve, and what the safety boundaries are.

- [Architecture](architecture.md)
- [Mediation model](mediation_model.md)
- [Action lifecycle](lifecycle.md)
- [Design principles](Design_Principles.md)
- [Glossary](glossary.md)

### Protocols

The formal contracts between components, and between the framework and plugins.

- [RCS](rcs.md)
- [MRS](mrs.md)
- [BPCS](bpcs.md)
- [EPS](eps.md)

### Development

Everything required to extend, test, and maintain RUNE.

- [Plugin development guide](plugin_dev_guide.md)
- [Bash library reference](bash_library_reference.md)
- [Testing guide](testing.md)
- [Style guide](STYLE_GUIDE.md)
- [API reference](api_reference.md)

### Reference

Large examples and schema consolidated for copy and paste.

- [JSON appendix](json_appendix.md)

## If you are evaluating RUNE for corporate operations

Start with:

- [Why RUNE](why_rune.md)
- [Architecture](architecture.md)
- [Security model](security_model.md)

Then skim the protocol pages and the JSON appendix as needed.

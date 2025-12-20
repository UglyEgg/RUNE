# Contributing

RUNE is built to be useful in real corporate IT and security operations. Contributions are welcome when they improve clarity, safety, and operational practicality.

## What to contribute

- documentation fixes and improvements
- protocol clarifications with concrete examples
- transport adapters (SSH improvements, SSM support)
- plugin development tooling
- test harnesses and sample plugins

## Guiding rules

- Protocol documents are contracts. Changes must be deliberate and versioned.
- Avoid breaking changes to message envelopes without a migration story.
- Favor explicit, boring behavior over clever implicit behavior.
- Add tests for any behavior that affects routing, output, or error handling.

## Pull requests

A good PR includes:

- a clear problem statement
- a short description of the operational impact
- documentation updates if behavior changes
- tests where applicable

## Security

If you find a security issue, do not publish it as an issue. Provide a responsible disclosure report through the repository’s security contact mechanism.

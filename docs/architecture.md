# Architecture

`python -m eval_scoreboard` delegates to `core.main`. Argument parsing and filesystem
access live at the boundary; the exported core functions own the behavior.
Results are plain Python data structures that can be serialized as JSON.

## Design decisions

- Standard library only: easy to run in a fresh agent environment.
- Explicit validation: bad input should fail predictably rather than be coerced.
- Stable ordering: examples and tests stay reproducible across machines.
- Read-only processing: input files are never modified.

## Extension strategy

Add a focused core function, test it using synthetic fixtures, then expose it via
the CLI. Keep the documented default behavior compatible where possible.

## Scope

Input files contain a run `name` and `cases`, each with string `id`, `expected`,
`actual`, and finite nonnegative numeric `latency_ms` and `cost_usd`. Run names and
case IDs must be unique. All runs must use identical IDs and expected answers.
Accuracy uses exact matching after Unicode case-folding and whitespace normalization.
Punctuation remains significant. Ranking sorts by accuracy descending, mean latency
ascending, then name. Costs come from the input, not current provider pricing.
Examples are synthetic and do not benchmark any real model. This metric suits short
deterministic answers; it does not measure open-ended response quality.
Exit codes: 0 success, 2 invalid input or I/O error.

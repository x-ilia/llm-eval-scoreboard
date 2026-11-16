# llm-eval-scoreboard

Compare saved LLM evaluation runs using exact-match accuracy, latency and declared cost.

A small, dependency-free Python project designed to be useful on its own and easy
for coding agents to understand. Runs locally; no API keys or services required.

## Quick start

Requires Python 3.11 or newer. From the repository root:

```sh
python -m eval_scoreboard examples/baseline.json examples/candidate.json
python -m unittest discover -s tests -v
```

Optional installation in a virtual environment:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
llm-eval-scoreboard --help
```

## Behavior and limits

Input files contain a run `name` and `cases`, each with string `id`, `expected`,
`actual`, and finite nonnegative numeric `latency_ms` and `cost_usd`. Run names and
case IDs must be unique. All runs must use identical IDs and expected answers.
Accuracy uses exact matching after Unicode case-folding and whitespace normalization.
Punctuation remains significant. Ranking sorts by accuracy descending, mean latency
ascending, then name. Costs come from the input, not current provider pricing.
Examples are synthetic and do not benchmark any real model. This metric suits short
deterministic answers; it does not measure open-ended response quality.
Exit codes: 0 success, 2 invalid input or I/O error.

## Layout

- `eval_scoreboard/core.py`: public functions and command-line interface.
- `tests/`: unit and command-line regression tests.
- `examples/`: small, synthetic inputs safe to share publicly.
- `AGENTS.md`: orientation and working conventions for coding agents.
- `docs/architecture.md`: data flow and extension points.

## Possible next steps

- Add per-case regression reports.
- Add configurable scoring strategies.
- Export a Markdown comparison table.

These are suggestions for future work, not implemented features.

## Development

Tests use the Python standard library. The CI workflow runs them on Python 3.11
and 3.12. Keep changes focused and add regression tests for behavior changes.
The project is intentionally small; it does not claim production readiness.

## License

MIT. See [LICENSE](LICENSE).

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from eval_scoreboard.core import compare, load_run, normalize

class EvalTests(unittest.TestCase):
    def write(self, root, name, cases):
        path = root / f"{name}.json"
        path.write_text(json.dumps({"name": name, "cases": cases}), encoding="utf-8")
        return path

    def row(self, **changes):
        return {"id": "one", "expected": "Paris", "actual": " paris ",
                "latency_ms": 10, "cost_usd": 0.001, **changes}

    def test_normalization(self):
        self.assertEqual(normalize("  HELLO\n world "), "hello world")

    def test_ranking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = self.write(root, "bad", [self.row(actual="London")])
            good = self.write(root, "good", [self.row()])
            result = compare([bad, good])
            self.assertEqual(result[0]["name"], "good")
            self.assertEqual(result[0]["accuracy"], 1)
            self.assertEqual(result[0]["total_cost_usd"], 0.001)

    def test_mismatched_dataset(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            one = self.write(root, "one", [self.row()])
            two = self.write(root, "two", [self.row(expected="Rome")])
            with self.assertRaises(ValueError):
                compare([one, two])

    def test_invalid_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            for cases in [[], [self.row(), self.row()], [self.row(latency_ms=True)],
                          [self.row(cost_usd=-1)], [self.row(cost_usd=float("nan"))]]:
                path = self.write(Path(tmp), "bad", cases)
                with self.assertRaises(ValueError):
                    load_run(path)

    def test_duplicate_run_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "one", [self.row()])
            with self.assertRaises(ValueError):
                compare([path, path])

    def test_cli(self):
        result = subprocess.run([sys.executable, "-m", "eval_scoreboard", "examples/baseline.json",
                                "examples/candidate.json"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)[0]["name"], "candidate")

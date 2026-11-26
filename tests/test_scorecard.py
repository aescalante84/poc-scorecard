import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import scorecard  # noqa: E402


def run(name):
    rubric = scorecard.load(os.path.join(ROOT, "rubric.json"))
    return scorecard.evaluate(rubric, scorecard.load(os.path.join(ROOT, "examples", name)))


class ScorecardTests(unittest.TestCase):
    def test_weights_sum_to_one(self):
        rubric = scorecard.load(os.path.join(ROOT, "rubric.json"))
        self.assertAlmostEqual(sum(d["weight"] for d in rubric["dimensions"]), 1.0)

    def test_ready_deal_is_go(self):
        r = run("deal_ready.json")
        self.assertEqual(r["verdict"], "GO")
        self.assertGreaterEqual(r["overall"], 70)
        self.assertEqual(r["blockers"], [])

    def test_fix_first_is_blocked_by_critical_dimensions(self):
        r = run("deal_fix_first.json")
        self.assertEqual(r["verdict"], "FIX FIRST")
        self.assertIn("Success metrics agreed", r["blockers"])
        self.assertIn("Economic buyer engaged", r["blockers"])

    def test_next_actions_start_with_blockers(self):
        r = run("deal_fix_first.json")
        self.assertIn(r["next_actions"][0]["dimension"], r["blockers"])

    def test_demo_request_is_not_yet(self):
        self.assertEqual(run("deal_not_yet.json")["verdict"], "NOT YET")

    def test_high_total_cannot_override_a_critical_blocker(self):
        rubric = scorecard.load(os.path.join(ROOT, "rubric.json"))
        scores = {d["id"]: {"level": 3, "evidence": "x"} for d in rubric["dimensions"]}
        scores["economic_buyer"] = {"level": 0}
        r = scorecard.evaluate(rubric, {"name": "t", "scores": scores})
        self.assertGreaterEqual(r["overall"], 70)
        self.assertEqual(r["verdict"], "FIX FIRST")

    def test_claim_without_evidence_is_capped_and_flagged(self):
        rubric = scorecard.load(os.path.join(ROOT, "rubric.json"))
        r = scorecard.evaluate(rubric, {"name": "t", "scores": {"champion": {"level": 3}}})
        champion = next(d for d in r["dimensions"] if d["id"] == "champion")
        self.assertEqual(champion["level"], 1)
        self.assertTrue(any("without evidence" in w for w in r["warnings"]))

    def test_rejects_bad_input(self):
        rubric = scorecard.load(os.path.join(ROOT, "rubric.json"))
        with self.assertRaises(ValueError):
            scorecard.evaluate(rubric, {"scores": {"nonsense": {"level": 1}}})
        with self.assertRaises(ValueError):
            scorecard.evaluate(rubric, {"scores": {"champion": {"level": 5, "evidence": "x"}}})


if __name__ == "__main__":
    unittest.main()

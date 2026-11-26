"""POC readiness scorecard. Stdlib only.

Usage:  python3 scorecard.py examples/deal_ready.json [--rubric rubric.json]

A deal file lists, per dimension, a level (0-3) and the evidence behind it.
Rules that make the score honest:
  * Level 2 or 3 requires evidence. A higher level with no evidence is capped at 1 and flagged.
  * Critical dimensions below level 2 block a GO, whatever the total.
  * The output names the blockers and the single next action per weak dimension.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def evaluate(rubric, deal):
    dims, warnings, rows = rubric["dimensions"], [], []
    given = deal.get("scores", {})
    unknown = set(given) - {d["id"] for d in dims}
    if unknown:
        raise ValueError(f"unknown dimensions in deal file: {sorted(unknown)}")
    total = 0.0
    for d in dims:
        entry = given.get(d["id"], {})
        level = int(entry.get("level", 0))
        if not 0 <= level <= 3:
            raise ValueError(f'{d["id"]}: level must be 0-3, got {level}')
        evidence = (entry.get("evidence") or "").strip()
        if level >= 2 and not evidence:
            warnings.append(f'{d["name"]}: level {level} claimed without evidence, capped at 1')
            level = 1
        score = round(level / 3 * 100)
        total += score * d["weight"]
        rows.append({"id": d["id"], "name": d["name"], "level": level, "score": score,
                     "critical": d["critical"], "evidence": evidence,
                     "meaning": d["levels"][str(level)], "ask": d["ask"]})
    overall = round(total)
    blockers = [r for r in rows if r["critical"] and r["level"] < 2]
    if blockers:
        verdict = "FIX FIRST"
    elif overall >= rubric["go_threshold"]:
        verdict = "GO"
    elif overall < rubric["not_yet_threshold"]:
        verdict = "NOT YET"
    else:
        verdict = "FIX FIRST"
    if overall < rubric["not_yet_threshold"] and blockers:
        verdict = "NOT YET"
    # Blockers come first, then the lowest-scoring dimensions.
    weakest = sorted((r for r in rows if r["level"] < 3),
                     key=lambda r: (not (r["critical"] and r["level"] < 2), r["score"]))[:3]
    return {"deal": deal.get("name", "unnamed"), "overall": overall, "verdict": verdict,
            "blockers": [b["name"] for b in blockers],
            "next_actions": [{"dimension": w["name"], "ask": w["ask"]} for w in weakest],
            "dimensions": rows, "warnings": warnings}


def render(result):
    out = [f'{result["deal"]}: {result["overall"]}/100 -> {result["verdict"]}', ""]
    for r in result["dimensions"]:
        mark = "*" if r["critical"] else " "
        out.append(f'{mark} {r["name"]:42s} L{r["level"]}  {r["meaning"]}')
    if result["blockers"]:
        out += ["", "Blockers (* = critical, needs level 2+): " + "; ".join(result["blockers"])]
    if result["warnings"]:
        out += ["", "Warnings:"] + [f"  - {w}" for w in result["warnings"]]
    out += ["", "Next actions:"] + [f'  - {a["dimension"]}: {a["ask"]}' for a in result["next_actions"]]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("deal")
    ap.add_argument("--rubric", default=os.path.join(HERE, "rubric.json"))
    ap.add_argument("--json", action="store_true", help="print machine-readable output")
    a = ap.parse_args()
    result = evaluate(load(a.rubric), load(a.deal))
    print(json.dumps(result, indent=2) if a.json else render(result))


if __name__ == "__main__":
    main()

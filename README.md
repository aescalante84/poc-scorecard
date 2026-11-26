# POC Readiness Scorecard

A small, opinionated tool for one decision: **should we start a proof of concept on this deal, or fix something first?**

**Author:** Alberto Escalante · [LinkedIn](https://www.linkedin.com/in/albertoantonioescalante/)
Vendor-neutral. The deals in `examples/` are fictional.

## Why it exists
A POC is expensive: weeks of engineering time, customer attention, and a public chance to fail. Most POCs that go nowhere had the same problem from day one: no agreed metric, no economic buyer, or no champion. This scorecard makes those gaps visible *before* the work starts, in a form a manager can review in two minutes.

It uses the MEDDPICC dimensions most sales teams already know, with three rules that keep the score honest:

1. **Evidence is required.** A dimension scored 2 or 3 must come with evidence (who said it, when). A claim with no evidence is capped at 1 and flagged.
2. **Critical dimensions can block a GO.** Pain, metrics, economic buyer, and champion must each reach level 2. A high total cannot hide a missing economic buyer.
3. **The output says what to do next.** Blockers first, then the weakest dimensions, each with the question to ask.

## Scoring scale
`0` unknown · `1` claimed, unverified · `2` verified by someone on the buyer side · `3` verified and written down or committed.

Full descriptions of each level for each dimension are in [`rubric.json`](rubric.json). Edit weights and thresholds there. The scoring logic lives in code, and the coaching content is data.

## Run it
```bash
python3 scorecard.py examples/deal_ready.json
python3 scorecard.py examples/deal_fix_first.json
python3 scorecard.py examples/deal_not_yet.json --json
python3 -m unittest discover -s tests        # 8 tests, stdlib only
```

## Example output
| Deal | Score | Verdict | Why |
|---|---|---|---|
| Harbor Foods (fictional) | 84 | **GO** | Costed pain, agreed metric, champion who introduced the CFO |
| Lakeside Retail (fictional) | 40 | **FIX FIRST** | Enthusiastic ops lead, but no agreed metric and no meeting with the economic buyer |
| Cedar Logistics (fictional) | 12 | **NOT YET** | A demo request with no pain, metric, or buyer |

## How I'd use it
- **Before committing resources:** score the deal with the account executive, and agree on the evidence together.
- **In deal review:** the "next actions" list is the agenda.
- **After a lost POC:** score it retrospectively. If the verdict would have been FIX FIRST, the process failed, not the product.

## Honest limits
- **It is a conversation tool, not a predictor.** The weights are my judgment, not fitted to win/loss data. With a few dozen closed deals you could test and tune them.
- **Evidence quality is still a human call.** The tool checks that evidence exists, not that it is good.
- **Thresholds are defaults.** A strategic account may justify a POC at FIX FIRST. The point is that the gap is a deliberate choice, not an accident.

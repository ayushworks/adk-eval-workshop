# Exercise 2 — LLM-as-a-Judge (~22 min)

**The idea:** trajectory tells you the agent took the right *steps*, but says nothing about whether
the reply was actually *good* — right amount, right timeline, real reason, right tone, and nothing
made up. You can't lexically match free-text quality at scale, so you use another model as a judge.
The lesson that matters: **a judge is only as good as its rubric.** Vague criteria ("rate
helpfulness 1–5") give you a confident number you can't trust; specific, decomposed, checkable
criteria give you a signal you can gate a release on.

We use two judge metrics, both of which run on a plain Gemini **API key** (no Vertex AI):

## What `test_config.json` checks

**`rubric_based_final_response_quality_v1`** — scores the agent's live reply against four explicit
rubrics, each phrased as a checkable assertion:

- `states_amount_when_refunded` — if a refund was issued, the reply states the exact dollar amount.
- `states_timeline_when_refunded` — if a refund was issued, the reply says when the money arrives.
- `gives_specific_reason` — the reply gives a clear, specific reason for the decision.
- `professional_tone` — the reply is warm and professional.

Notice the rubrics are *specific and decomposed* — each one is independently true or false, so the
score is explainable. That's the whole difference between a judge you can trust and one you can't.

**`hallucinations_v1`** — a separate check that segments the reply into individual claims and
verifies each against the **trusted evidence** (the user's request and the actual tool outputs). It
catches the agent inventing a policy detail, a refund window, or an amount the tools never returned.
This is the natural division of labor: the rubrics check *"did the reply include what a good answer
needs,"* and hallucinations checks *"did the reply state anything not backed by the tools."*

## Run it

```bash
adk eval refund_agent exercises/02_judge/judge.evalset.json \
  --config_file_path exercises/02_judge/test_config.json
```

What happens underneath: the agent is **run live** on each user message (`A1001` → refund, `A1002`
→ decline), producing a real reply and real tool calls. The judge model then scores those *actual*
replies against the rubrics, and `hallucinations_v1` checks them against the tool outputs. (The
metrics ignore any reference answer in the eval set — they grade what the agent actually said.)

## Read the output

The detailed results show, per case: the `prompt`, the `actual_response`, the per-rubric scores with
the judge's reasoning, and the hallucination score. Read the **reasoning** column — that's where you
see *why* the judge scored each rubric the way it did, which is how you sanity-check that the judge
itself is behaving.

> Tip: `num_samples` is set to 5 so the judge is sampled multiple times and the score is stable. A
> judge that disagrees with itself run-to-run is its own kind of broken — pin the model and raise the
> sample count for a score you can rely on.

**Takeaway:** the judge is only as good as its rubric — specific, decomposed, checkable criteria,
plus a pinned model and enough samples. Then it's a signal you can put in CI (Section 4).

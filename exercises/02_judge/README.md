# Exercise 2 — LLM-as-a-Judge (~22 min)

**The idea:** trajectory tells you the agent took the right *steps*, but says
nothing about whether the reply was actually *good* — right amount, right
timeline, real reason, right tone, no invented policy. You can't lexically
match free-text quality at scale, so you use another model as a judge. The catch:
**a poorly designed judge is worse than no judge.** A vague rubric hands you a
confident green score you can't trust.

`test_config.json` here ships a deliberately bad judge: one fuzzy rubric, *"The
response should be helpful and good."* You're going to feel why that fails, then
fix it.

## Part A — watch the bad judge pass a bad answer (7 min)

1. Run the vague judge against the agent:

   ```bash
   adk eval refund_agent exercises/02_judge/judge.evalset.json \
     --config_file_path exercises/02_judge/test_config.json
   ```

   It passes. Fine.

2. Now **break the agent's reply quality.** In `refund_agent/agent.py`, delete
   the line in the instruction that says to *state the refund amount and the
   expected timeline*. Re-run the same eval.

   The agent now answers *"Sure, I've processed that for you."* — no amount, no
   timeline, useless to a real customer. **The vague judge still says it's
   good.** That green score is a lie. This is the whole point of the section.

## Part B — design a judge you can trust (12 min)

Replace the single fuzzy rubric in `test_config.json` with several *specific,
checkable* ones. Good rubrics read like assertions, not vibes. Think about what
a genuinely good refund reply must contain. Some to get you started:

- If a refund was issued, the response states the exact dollar amount.
- If a refund was issued, the response states when the money arrives.
- The response gives a clear, specific reason for the decision.
- The response does not state any policy detail the tools did not return.
- The tone is warm and professional.

Also tighten the **judge config itself** — pin the `judge_model` and raise
`num_samples` so the score is stable across runs. A judge that disagrees with
itself run to run is its own kind of broken.

Re-run with the still-weakened agent: a good judge now **fails** the
amount/timeline rubrics. Restore the agent instruction and re-run: it passes
again. That flip — from a true fail to a true pass — is what a trustworthy judge
looks like.

> The tightened config is in `solutions/02_judge/test_config.json` if you want to
> compare or catch up.

**Takeaway:** the judge is only as good as its rubric. Specific, decomposed,
checkable criteria + a pinned model + enough samples. Then it's a signal you can
gate a release on (Section 4).

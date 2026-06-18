# Exercise 1 — Trajectory evaluation (~18 min)

**The idea:** a trajectory eval asserts the agent took the *right steps* — the
right tool calls, in the right order — not just that the final text looks
plausible. This is the layer that catches dangerous behavior an output check
would wave straight through (e.g. refunding before checking the policy).

You'll work in `starter.evalset.json`. Case **A1001** is filled in for you as a
worked example. Copy its shape for the rest.

## Part A — capture a golden case from the UI (5 min)

The best golden cases come from real runs, not hand-typed JSON.

1. From the repo root, launch the dev UI:

   ```bash
   adk web
   ```

2. Pick `refund_agent`, then send: *"Hi, I'd like a refund for my order
   A1001."* Watch the tool calls in the trace on the right.
3. Save the session as an eval case (the **Eval** tab → save current session).
   Open the file it created and notice it captured exactly what's in the A1001
   case here: the user message, the tool trajectory, and the final response.
   **That capture is your golden case.**

## Part B — fill in the two TODO cases (8 min)

In `starter.evalset.json`, two cases have `TODO` placeholders. Replace them with
the correct expected `tool_uses` (and a sensible expected final response):

- **A1002** — valid order, but placed 2026-04-01, *outside* the 30-day window.
  What tools should fire? Critically: should `issue_refund` be one of them?
- **A1004** — this order ID does not exist. How many tools fire before the agent
  has to stop and ask for a valid ID?

Each `tool_uses` entry looks like:

```json
{ "name": "get_order_status", "args": { "order_id": "A1002" } }
```

Then run it:

```bash
adk eval refund_agent exercises/01_trajectory/starter.evalset.json \
  --config_file_path exercises/01_trajectory/test_config.json
```

All three cases should pass (`tool_trajectory_avg_score = 1.0`).

> Stuck? The complete answer is in `solutions/01_trajectory/`. Copy it, get
> green, and move on — don't fall behind.

## Part C — make it break (5 min)

This is the part that makes the lesson stick. Open `refund_agent/agent.py` and
**weaken the instruction** so the agent skips the policy check — delete step 2,
or change it to "issue the refund immediately after looking up the order."

Re-run the eval. Watch the A1001/A1003 trajectories now fail: the agent calls
`issue_refund` without `get_refund_policy`. An output-only check would still
pass that answer — it *reads* fine — but the trajectory eval catches the unsafe
shortcut. Restore the instruction when you're done.

**Takeaway:** trajectory tests guard *behavior*. They are deterministic, fast,
and they belong in CI (Section 4).

# Agent Evaluation with Google ADK — Workshop

A hands-on, 90-minute tour of how to evaluate agents properly. We build one small
agent and evaluate it three ways:

1. **Trajectory evaluation** — assert the agent took the right *steps* and tool
   calls, not just that the output looks plausible.
2. **LLM-as-a-Judge** — score response *quality* at scale, and see why a poorly
   designed judge is worse than no judge at all.
3. **Eval as an engineering discipline** — move eval out of a notebook into a CI
   pipeline that catches regressions before users do.

The examples use Google's Agent Development Kit (ADK), but the patterns are
framework-agnostic.

---

## Running on a restricted network? Use Colab (recommended for locked-down laptops)

If your machine's network blocks the Google AI endpoints (`generativelanguage.googleapis.com`,
`aiplatform.googleapis.com`) — common on corporate laptops — the local setup below won't be able to
reach a model. **Run the workshop in Google Colab instead:** the model calls execute on Google's
network, not your laptop, so your API key works there even when it's blocked on the office network.

[**Open the workshop notebook in Colab**](https://colab.research.google.com/github/ayushworks/adk-eval-workshop/blob/main/adk_eval_workshop_colab.ipynb)
&nbsp;(`adk_eval_workshop_colab.ipynb`)

For the Colab path you only need a **browser that can reach `colab.research.google.com`** and a
Google account — no local Python, Git, or install. Make a copy (File → Save a copy in Drive) and run
the cells top to bottom. (Verify a real ING laptop can open Colab before the session; if Colab itself
is blocked, fall back to a provisioned cloud VM.) The notebook is self-contained — it writes the same
agent and eval files you see in this repo. `adk web` is replaced by a code cell that runs the agent
and prints its trajectory.

The local setup below is for anyone **not** on a restricted network.

---

## Setup (do this BEFORE the workshop — ~15 min)

You need **Python 3.10+** and **Git**. You do **not** need an API key in advance —
we hand those out at the session.

> **`python` vs `python3`:** on macOS and many Linux setups, `python` isn't on
> the PATH — use `python3` (and `pip3`) instead everywhere in this README. Quick
> check: `python --version`; if that errors, run `python3 --version`. The rest of
> these docs write `python` for brevity.

```bash
# 1. Clone
git clone <REPO_URL> adk-eval-workshop
cd adk-eval-workshop

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install pinned dependencies
pip install -r requirements.txt

# 4. Verify your setup
python check_setup.py
```

You're ready when the last line reads:

```
READY ✅  You're all set for the workshop.
```

If it says `NOT READY`, the script tells you exactly what to fix. Still stuck?
Reply to the prerequisites email before the session — much easier to sort out
beforehand than live.

### At the workshop: add your key

We'll give you a model API key on the day. Then:

```bash
cp .env.example .env
# paste the key into .env as GOOGLE_API_KEY
```

---

## The agent we're evaluating

A **customer-support agent that handles refund requests** (`refund_agent/`). A
customer messages in plain language; the agent must find the order, check the
refund policy, and either issue the refund or explain why not.

It has three tools, all deterministic local mocks (no live APIs, so evals are
reproducible):

| Tool | Type | Role |
| --- | --- | --- |
| `get_order_status(order_id)` | read | Find the order; can fail if the ID is unknown |
| `get_refund_policy(category)` | read | The eligibility check |
| `issue_refund(order_id, amount)` | **write** | The risky action — must come last, and only if eligible |

The **correct trajectory** is always: look up the order → check the policy →
*only if eligible* issue the refund. The five seed orders each exercise a
different branch:

| Order | Situation | Correct behavior |
| --- | --- | --- |
| `A1001` | valid, within window | refund issued |
| `A1002` | valid, **outside** the window | declined, no refund |
| `A1003` | valid, arrived damaged | refund issued (damage overrides window) |
| `A1004` | does not exist | ask for a valid ID, no refund |
| `A1005` | already refunded | no second refund |

---

## Repo layout

```
refund_agent/                 the agent under test
  agent.py                    root_agent + the instruction (the "contract")
  tools.py                    the 3 mock tools
  data.py                     5 seed orders + refund policy
eval/                         the reference / CI eval
  trajectory.evalset.json     all 5 golden cases
  test_config.json            thresholds (tool_trajectory_avg_score = 1.0)
  test_refund_agent.py        the same eval as a pytest test (what CI runs)
exercises/                    what YOU build during the session
  01_trajectory/              fill in TODO cases, then make it break
  02_judge/                   turn a vague rubric into a trustworthy judge
solutions/                    completed versions — copy if you fall behind
.github/workflows/eval.yml    eval as a CI gate
check_setup.py                pre-workshop setup check
```

---

## How we'll use it (the three sections)

### 0. Walkthrough + see it run

Read `refund_agent/agent.py` top to bottom, then launch the dev UI and try it:

```bash
adk web
```

Open `refund_agent`, send *"I'd like a refund for order A1001,"* and watch the
tool trace. Save the session as an eval case — that capture is your first golden
case.

### 1. Trajectory evaluation

Run the reference eval:

```bash
adk eval refund_agent eval/trajectory.evalset.json \
  --config_file_path eval/test_config.json
```

Then do **`exercises/01_trajectory/`** — fill in two TODO cases and watch a
weakened agent fail the trajectory check.

### 2. LLM-as-a-Judge

Do **`exercises/02_judge/`** — run a deliberately vague judge, watch it pass a
bad answer, then redesign it into rubrics you can actually trust.

### 3. Eval as an engineering discipline

The reference eval is also a pytest test:

```bash
pytest eval/ -v
```

That's exactly what `.github/workflows/eval.yml` runs on every push and PR. Open
a PR that weakens the agent and watch the check go red — a regression caught
before it ships.

---

## Quick command reference

```bash
python check_setup.py                                   # verify setup
adk web                                                 # dev UI
adk eval refund_agent eval/trajectory.evalset.json \
  --config_file_path eval/test_config.json              # run trajectory eval
pytest eval/ -v                                         # run eval as a test (CI)
```

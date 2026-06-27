#!/usr/bin/env python3
"""Pre-workshop setup check.

Run this BEFORE the session:

    python check_setup.py

You're ready when the last line says:  READY

It verifies your Python version, that the dependencies installed, that the
example agent imports, and that the eval files are valid. It does NOT need an
API key — we hand those out at the workshop, so a missing key is fine here.
"""

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).parent.resolve()
PASS = "[ ok ]"
FAIL = "[FAIL]"
problems = []


def check(label, ok, hint=""):
    print(f"{PASS if ok else FAIL} {label}")
    if not ok and hint:
        print(f"        -> {hint}")
    if not ok:
        problems.append(label)
    return ok


# 1. Python version
v = sys.version_info
check(
    f"Python {v.major}.{v.minor} (need 3.10+)",
    v >= (3, 10),
    "Install Python 3.10 or newer and recreate your virtualenv.",
)

# 2. Dependencies import
try:
    import google.adk  # noqa: F401
    import google.adk.evaluation.agent_evaluator  # noqa: F401

    check("google-adk installed", True)
except Exception as e:  # pragma: no cover
    check("google-adk installed", False, f"pip install -r requirements.txt  ({e})")

# The [eval] extra (pandas, rouge-score, ...) is needed to RUN evals. The agent
# imports without it, so check the extra explicitly — this is a common gotcha.
try:
    import pandas  # noqa: F401
    import rouge_score  # noqa: F401

    check("google-adk[eval] extras installed", True)
except Exception as e:  # pragma: no cover
    check(
        "google-adk[eval] extras installed",
        False,
        'pip install "google-adk[eval]==1.35.2"  (or: pip install -r requirements.txt)'
        f"  ({e})",
    )

for mod in ("pytest", "pytest_asyncio"):
    try:
        __import__(mod)
        check(f"{mod} installed", True)
    except Exception as e:  # pragma: no cover
        check(f"{mod} installed", False, f"pip install -r requirements.txt  ({e})")

# 3. The example agent imports and looks right
try:
    sys.path.insert(0, str(REPO))
    from refund_agent import root_agent

    tool_names = sorted(t.name for t in root_agent.tools)
    expected = ["get_order_status", "get_refund_policy", "issue_refund"]
    check(
        f"refund_agent loads with 3 tools {tool_names}",
        tool_names == expected,
        "Agent or tools failed to import. Did all files download?",
    )
except Exception as e:
    check("refund_agent imports", False, f"{e}")

# 4. Eval files are valid JSON and parse against ADK models
try:
    from google.adk.evaluation.eval_config import EvalConfig
    from google.adk.evaluation.eval_set import EvalSet

    EvalSet.model_validate_json((REPO / "eval/trajectory.evalset.json").read_text())
    EvalConfig.model_validate_json((REPO / "eval/test_config.json").read_text())
    check("golden evalset + config are valid", True)
except Exception as e:
    check("golden evalset + config are valid", False, f"{e}")

# 5. Friendly heads-up about the key (not a failure)
import os

if not os.environ.get("GOOGLE_API_KEY"):
    print(
        f"{PASS} model key not set yet — that's expected; you'll get one at the workshop"
    )

print()
if problems:
    print(f"NOT READY — {len(problems)} item(s) need attention above.")
    print("Fix them, or reply to the prerequisites email and we'll help.")
    sys.exit(1)
else:
    print("READY \N{WHITE HEAVY CHECK MARK}  You're all set for the workshop.")
    sys.exit(0)

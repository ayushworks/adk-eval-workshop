"""The same golden eval, expressed as a pytest test.

This is the bridge from "I ran an eval in the terminal" to "eval is part of my
engineering pipeline". `adk eval ...` and this test run the *identical*
trajectory.evalset.json against the *identical* agent — but because this is a
pytest test, CI can run it on every commit and fail the build on a regression.

Run locally:
    pytest eval/test_refund_agent.py -v

This is what the GitHub Actions workflow (.github/workflows/eval.yml) invokes.
"""

import pathlib

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator

HERE = pathlib.Path(__file__).parent
EVALSET = HERE / "trajectory.evalset.json"


@pytest.mark.asyncio
async def test_refund_agent_trajectory():
    """Assert the agent takes the correct tool trajectory on all golden cases.

    AgentEvaluator reads test_config.json sitting next to the evalset to learn
    the thresholds (here: tool_trajectory_avg_score must be a perfect 1.0).
    """
    await AgentEvaluator.evaluate(
        agent_module="refund_agent",
        eval_dataset_file_path_or_dir=str(EVALSET),
    )

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

## Workshop setup - Use Colab

Most corporate laptops block the Google AI endpoints (`generativelanguage.googleapis.com`,
`aiplatform.googleapis.com`) and so the local machine won't be able to
reach a model. As an alternative we use Google Colab to execute python code in browser. 

[**Open the workshop notebook in Colab**](https://colab.research.google.com/github/ayushworks/adk-eval-workshop/blob/main/adk_eval_workshop_colab.ipynb)
&nbsp;(`adk_eval_workshop_colab.ipynb`)

For the Colab path you only need a **browser that can reach `colab.research.google.com`** and a
Google account — no local Python, Git, or install. Make a copy (File → Save a copy in Drive) and run
the cells top to bottom. The notebook is self-contained — it writes the same
agent and eval files you see in this repo. `adk web` is replaced by a code cell that runs the agent
and prints its trajectory.
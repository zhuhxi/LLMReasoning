# reasoning-agent

`reasoning-agent` is a small local Python project that demonstrates how a reasoning-oriented LLM agent can combine chain-of-thought, least-to-most prompting, and self-consistency voting on top of a local Ollama model.

## Why this project exists

This repo is intentionally practical. It connects classic reasoning-prompting ideas from the literature to an agent-style workflow that a student can run locally, inspect, and extend:

- Chain-of-Thought for direct step-by-step reasoning
- Least-to-Most for decomposition followed by sequential solving
- Self-consistency for multi-sample answer voting
- A simple router that chooses a strategy when `--strategy auto` is used

The code favors a complete end-to-end implementation over heavy abstractions.

## Assumptions

- Python 3.11+ is available locally.
- Ollama is running locally at `http://localhost:11434` unless `OLLAMA_BASE_URL` is overridden.
- The default model is `llama3.1:8b`, but any Ollama text model that follows instructions reasonably well can be used.
- Prompt adherence is not perfect. The implementation expects the model to usually end with `Final Answer: <answer>`.
- If majority voting ties, the system picks the answer that appeared first among the samples. This is deterministic and documented in code and tests.
- Benchmark accuracy depends strongly on the chosen model. Smaller local models may produce weak decompositions or inconsistent answer formatting.

## Project layout

```text
app/
  main.py
  config.py
  models.py
  ollama_client.py
  prompts/
  strategies/
  pipeline/
  utils/
data/
  examples.json
  benchmark.json
tests/
requirements.txt
README.md
```

## Install and setup

### 1. Install Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Install Ollama

See the official install instructions at [ollama.com](https://ollama.com/download).

After installation, start the server:

```bash
ollama serve
```

### 3. Pull a compatible model

```bash
ollama pull llama3.1:8b
```

You can also set a different local model:

```bash
export OLLAMA_MODEL=qwen2.5:7b
```

## Usage

### Solve one question with automatic routing

```bash
python -m app.main --question "Elsa has 3 apples, buys 4 more, then gives away 2. How many apples does she have now?" --strategy auto --samples 5
```

### Force chain-of-thought

```bash
python -m app.main --question "What is 18 minus 7 plus 3?" --strategy cot --samples 1
```

### Force least-to-most

```bash
python -m app.main --question "A bus has 18 passengers. At the first stop, 6 get off and 4 get on. How many passengers are on the bus now?" --strategy l2m --samples 5
```

### Run both strategies and compare

```bash
python -m app.main --question "Tom has 3 bags with 4 marbles in each bag. How many marbles does he have?" --strategy both --samples 3
```

### Run benchmark evaluation

```bash
python -m app.main --benchmark data/benchmark.json --output benchmark_results.json
```

The benchmark command compares:

- single-run CoT
- self-consistency CoT
- single-run Least-to-Most
- self-consistency Least-to-Most

Results are printed and also saved to JSON.

## Example output

```json
{
  "chosen_strategy": "l2m",
  "runs": [
    {
      "strategy": "l2m",
      "sample_index": 0,
      "trace": "Decomposition:\n1. Add the apples Elsa bought.\n2. Subtract the apples she gave away.\n\nSubproblem: Add the apples Elsa bought.\nElsa has 7 apples after buying more.\n\nSubproblem: Subtract the apples she gave away.\nSubtract 2 from 7.\nFinal Answer: 5",
      "final_answer": "5",
      "normalized_answer": "5",
      "metadata": {
        "subproblems": [
          "Add the apples Elsa bought.",
          "Subtract the apples she gave away."
        ]
      }
    }
  ],
  "vote_counts": {
    "5": 1
  },
  "final_selected_answer": "5"
}
```

## Tests

Run the full test suite with:

```bash
pytest
```

The tests cover:

- answer extraction and normalization
- majority voting behavior
- rule-based router behavior
- least-to-most sequential solve flow
- CLI smoke behavior without needing a live Ollama server

## Environment variables

- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `OLLAMA_TEMPERATURE`
- `OLLAMA_TIMEOUT`
- `OLLAMA_MAX_RETRIES`
- `REASONING_AGENT_DEFAULT_SAMPLES`

## Limitations

- This is a prompting-based reasoning agent, not a formal symbolic solver.
- It returns intermediate reasoning traces, which is useful for demos but can be noisy or inconsistent across models.
- The router is intentionally simple and rule-based.
- The answer extractor is robust for short answers, numbers, and simple text, but it is not a full semantic parser.
- Self-consistency improves reliability only when the underlying model can already solve a reasonable fraction of the tasks.

## Future improvements

- Add benchmark slices by category and error analysis summaries.
- Add a prompt-based or learned router.
- Add confidence scoring beyond majority voting.
- Add better structured output parsing for harder reasoning tasks.
- Add optional local caching for repeated benchmark runs.

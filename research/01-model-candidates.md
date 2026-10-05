# 01 · Model candidates

Source: OpenRouter's public model list (`https://openrouter.ai/api/v1/models`, no key needed), pulled on
28 September 2026. The snapshot is saved as `openrouter-models-2026-09-28.json`.

## What is available

- 458 models in total; 288 accept image input.
- After removing routers, image-generation models, safety classifiers, dated duplicate snapshots and
  `:batch` / `:thinking` variants, about 200 text-output vision models remain.

## Price is per token, not per image

OpenRouter lists prices per million input and output tokens. Each provider turns an image into a different
number of tokens, so list price is a poor guide to cost per image. Median input tokens per image in our run:

| Model | Tokens per image |
|---|---|
| deepseek-v4.1-flash | 1,038 |
| gemini-3.1 / 3.5-flash-lite | 1,113 |
| qwen3.6-35b-a3b, qwen3.5-9b | 1,284–1,380 |
| ling-3.0-flash-vl, qwen3.8-flash, mimo-v2.6-flash, nemotron | about 1,800 |
| gpt-6-luna, mistral-small-3.2 | about 2,150 |
| kimi-k2.5, glm-5.3-flash | about 2,350 |
| gpt-5-nano | 2,648 |

The benchmark therefore records the cost OpenRouter actually billed (`usage.cost`) for every call.

## How the 14 were chosen

The first shortlist had about 25 models in tiers: free, under $0.50, $0.50–2 and $2–6 combined price per
million tokens, plus three expensive reference models. Then:

- Published leaderboards (see 03) already covered many open-weight Qwen models, so the list was trimmed to
  the models with published scores worth confirming plus the cheap closed models that had no OCR data.
- The expensive reference models were dropped at the user's request: Claude Sonnet 5, Gemini 3.1 Pro,
  GPT-5.6 Sol. Every item has ground truth, so each model gets an absolute score without them.
- Gemini 3.8 Flash ($0.75 / $3.75) and Claude Haiku 4.5 ($1 / $5) were also dropped as too expensive for
  the goal.

## Final list (prices in $ per million tokens, input / output)

| Model | Price | Why included |
|---|---|---|
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | free | top of OCRBench v2 among small models |
| `inclusionai/ling-3.0-flash-vl` | 0.021 / 0.062 | cheapest paid vision model |
| `qwen/qwen3.5-9b` | 0.10 / 0.15 | small open model with strong published scores |
| `openai/gpt-5-nano` | 0.05 / 0.40 | cheapest OpenAI |
| `openai/gpt-6-luna` | 0.10 / 0.50 | cheap current OpenAI |
| `mistralai/mistral-small-3.2-24b-instruct` | 0.094 / 0.25 | cheap open model |
| `deepseek/deepseek-v4.1-flash` | 0.035 / 0.29 | cheap, no OCR data |
| `xiaomi/mimo-v2.6-flash` | 0.14 / 0.28 | cheap, no OCR data |
| `z-ai/glm-5.3-flash` | 0.15 / 0.50 | cheap, no OCR data |
| `qwen/qwen3.8-flash` | 0.15 / 0.47 | newest cheap Qwen |
| `qwen/qwen3.6-35b-a3b` | 0.15 / 1.00 | best published OCRBench v2 score per dollar |
| `google/gemini-3.1-flash-lite` | 0.25 / 1.50 | cheap Google |
| `google/gemini-3.5-flash-lite` | 0.30 / 2.50 | newer cheap Google |
| `moonshotai/kimi-k2.5` | 0.45 / 2.25 | top self-reported OCRBench v1 score |

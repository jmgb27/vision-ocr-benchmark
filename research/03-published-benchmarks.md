# 03 · Published benchmarks

Checked on 28 September 2026 to see whether existing results made our own run unnecessary.

## What exists for models on our list

| OpenRouter model | Price ($/M in/out) | OCRBench v1 | OCRBench v2 (English) |
|---|---|---|---|
| `nvidia/nemotron-3-nano-omni-30b-a3b` | free | — | 65.8 |
| `qwen/qwen3.5-9b` | 0.10 / 0.15 | — | 58.7 |
| `qwen/qwen3-vl-32b-instruct` | 0.10 / 0.42 | 89.5 | — |
| `qwen/qwen3-vl-8b-instruct` | 0.12 / 0.46 | 89.6 | — |
| `qwen/qwen3-vl-30b-a3b-instruct` | 0.15 / 0.60 | 90.3 | — |
| `qwen/qwen3.6-35b-a3b` | 0.15 / 1.00 | — | 65.5 |
| `qwen/qwen3.5-35b-a3b` | 0.16 / 1.30 | 91.0 | 65.3 |
| `qwen/qwen3-vl-235b-a22b-instruct` | 0.21 / 1.90 | 92.0 | — |
| `bytedance-seed/seed-1.6` | 0.25 / 2.00 | — | 62.2 |
| `moonshotai/kimi-k2.5` | 0.45 / 2.25 | 92.3 (top) | — |
| `google/gemini-2.5-pro` | 1.25 / 10 | — | 59.3 |
| `openai/gpt-5` | 1.25 / 10 | — | 55.5 |

For reference, Gemini 3 Pro Preview scores 63.4 on OCRBench v2 (English), below the free Nemotron model.
Qwen3-VL-4B-Instruct scores 88.1 on OCRBench v1.

No published OCR scores existed for: GPT-6 Luna, GPT-5-nano, Gemini 3.1 / 3.5 Flash Lite, the Gemini 3.x
Flash models, Claude Haiku 4.5, Claude Sonnet 5, MiMo v2.6 Flash, Ling 3.0 Flash VL, DeepSeek V4.1 Flash,
Mistral Small, GLM 5.3 Flash, Qwen3.7 / 3.8 Flash. That is most of the cheap tier.

## Why published numbers were not enough

- All 24 OCRBench v1 scores on llm-stats are self-reported by the model vendors; none are independently verified.
- None of the leaderboards track cost, which varies widely per image (see 01).
- OpenRouter routes open-weight models to many hosts, some running compressed versions, so accuracy through
  OpenRouter can differ from published figures. Our run found signs of this (see 04).
- None test marketplace screenshots.
- OmniAI's JSON-extraction leaderboard, the closest match to our use case, was last updated in March 2025.

## How our results compare

Our run broadly agreed with the published picture for the Qwen models (strong on OCR). It also found that
several cheap closed models with no published scores (Gemini 3.1 Flash Lite, Ling 3.0 Flash VL, Qwen3.8
Flash) beat every published open model on our mix.

## Sources

- [OCRBench v2 leaderboard (2026.06)](https://99franklin.github.io/ocrbench_v2/)
- [OCRBench v1 on llm-stats](https://llm-stats.com/benchmarks/ocrbench)
- [OmniAI OCR benchmark](https://github.com/getomni-ai/benchmark)
- [OpenCompass Open VLM Leaderboard](https://opencompass-open-vlm-leaderboard.hf.space/)

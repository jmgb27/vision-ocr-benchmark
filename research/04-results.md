# 04 · Results

Run on 28 September 2026: 14 models × 200 images through OpenRouter, $2.67 in total including the pilot and
retries.

Settings:

- temperature 0
- `reasoning: {effort: "low"}`
- `max_tokens` 16,000 (8,000 in the pilot)
- images at most 1,600 px on the long side

Failed or empty answers were retried once in a second pass.

## Overall

Overall is the mean of OCRBench accuracy and OmniAI JSON field accuracy. Cost is OpenRouter's billed cost.

| Model | OCR % | JSON % | Overall % | $ per 1k images | Median seconds |
|---|---|---|---|---|---|
| gemini-3.1-flash-lite | 92.0 | 94.1 | **93.1** | 0.86 | 3.0 |
| gemini-3.5-flash-lite | 90.0 | 92.0 | 91.0 | 0.87 | 1.9 |
| qwen3.8-flash | 89.3 | 92.0 | 90.7 | 0.47 | 3.7 |
| ling-3.0-flash-vl | 92.0 | 89.0 | 90.5 | **0.11** | 4.4 |
| glm-5.3-flash | 88.7 | 91.9 | 90.3 | 0.55 | 2.6 |
| kimi-k2.5 | 83.3 | 92.3 | 87.8 | 5.10 | 7.7 |
| qwen3.6-35b-a3b | 90.7 | 82.6 | 86.6 | 1.01 | 5.8 |
| qwen3.5-9b | 89.3 | 81.7 | 85.5 | 0.39 | 10.2 |
| mimo-v2.6-flash | 79.3 | 88.7 | 84.0 | 0.41 | 13.7 |
| deepseek-v4.1-flash | 80.0 | 86.8 | 83.4 | 1.46 | 3.5 |
| gpt-6-luna | 66.0 | 92.3 | 79.1 | 0.37 | 3.1 |
| nemotron-3-nano-omni (free) | 85.3 | 67.4 | 76.4 | 0 | 11.4 |
| mistral-small-3.2 | 66.7 | 81.5 | 74.1 | 0.25 | 3.0 |
| gpt-5-nano | 64.7 | 42.6 | 53.7 | 0.28 | 4.7 |

Per-category scores are in `../report.md`. Every answer is in `../results.jsonl`.

## Findings

### 1. The top five are effectively tied on quality

Gemini 3.1 Flash Lite, Gemini 3.5 Flash Lite, Qwen3.8 Flash, Ling 3.0 Flash VL and GLM 5.3 Flash are within
3 points. With 200 images that is close to noise, so choose among them on price, speed and hosting.

### 2. Thinking costs time and money without improving accuracy here

- **No hidden reasoning:** Gemini 3.5 Flash Lite, GLM 5.3 Flash, GPT-6 Luna and Mistral produce 5–12 output
  tokens with zero reasoning; they are the fastest.
- **Heavy reasoning:** Nemotron, Qwen3.6, Qwen3.5-9B, MiMo and Kimi spend 160–300 reasoning tokens per image
  without scoring higher.
- **Slowest 10% of calls:** Nemotron 206 s, Qwen3.5-9B 94 s, Kimi 70 s; Gemini 3.5 Flash Lite 3 s.
- **Blank answers:** Qwen3.5-9B, DeepSeek and MiMo occasionally returned blank answers because reasoning used
  the whole token allowance, even at low effort and 16,000 tokens.

### 3. Consistency on business documents (out of 50)

| Model | Perfect extractions | Badly failed (<50% of fields) |
|---|---|---|
| gemini-3.1-flash-lite | 31 | 2 |
| gemini-3.5-flash-lite | 30 | 3 |
| qwen3.8-flash | 28 | 3 |
| kimi-k2.5 | 28 | 3 |
| glm-5.3-flash | 27 | 3 |
| ling-3.0-flash-vl | 25 | 4 |
| gpt-6-luna | 23 | 2 |
| mistral-small-3.2 | 12 | 7 |
| nemotron (free) | 11 | 14 |
| gpt-5-nano | 3 | 30 |

GPT-5-nano often returned empty lists, for example `{"checks": []}`.

### 4. Numbers are the main weak point

Handwritten digit strings, the stand-in for phone numbers and prices:

- Ling 87%, Qwen3.5-9B and Gemini 3.5 Flash Lite 80%, Gemini 3.1 / Qwen3.8 / GLM 73%.
- Kimi and Nemotron 40%, MiMo and DeepSeek 33%, Mistral 13%.
- GPT-6 Luna and GPT-5-nano 7%. GPT-6 Luna misreads digits outright (7500 → 2500, 1570 → 5720).

Random letter strings (stand-in for SKUs and codes): 100% for Gemini 3.1, Ling, GLM and Qwen3.6; 7% for
GPT-5-nano and 33% for Mistral.

### 5. Hardest document types

Average across all models:

- **Hardest:** bank cheques 59%, credit-card statements 61%, glossaries 69%. These are dense tables full of numbers.
- **Easiest:** patient intake, tables, inspection sheets, pay-in sheets and leases, all 95%+. These are clean
  labelled layouts.

### 6. The serving host may affect accuracy

OpenRouter spread open-weight models across many hosts, and scores differed by host:

- DeepSeek V4.1 Flash: Together 72% (61 calls) versus CoreWeave 90% (33) and Parasail 86% (59).
- Qwen3.6-35B: Darkbloom 81% (58) versus AkashML 94% (32) and Venice 98% (22).
- GLM 5.3 Flash: stable at 90–92% on its main hosts.

Items were not split evenly across hosts, so this is not proof. It is consistent with some hosts running
compressed versions. For open-weight models in production, pin a tested host with
`provider: {only: [...]}`. Gemini (Google only) and Qwen3.8 Flash (Alibaba only) avoid the issue.

### 7. Some failures are the benchmark's fault

Nine items defeated almost every model, including:

- an expected answer that is only part of an address
- a watermark (`www.shutterstock.com 3003`) as the expected answer
- ambiguous handwritten digits

These cost every model equally, so the ranking holds, but true accuracy is a few points higher than shown.

## Recommendations

| Need | Pick | Why |
|---|---|---|
| Lowest cost | `inclusionai/ling-3.0-flash-vl` | 90.5% at $0.11 per 1k, best on digits; pin one host (Novita or DeepInfra) |
| Most reliable | `google/gemini-3.1-flash-lite` | 93.1%, most perfect extractions, one host, 3 s |
| Fastest | `google/gemini-3.5-flash-lite` | 91.0%, 1.9 s median, 3 s for the slowest 10% |
| Balanced | `qwen/qwen3.8-flash` | 90.7% at $0.47 per 1k, one host |
| Avoid for numbers | GPT-6 Luna, GPT-5-nano, Mistral Small | 7–13% on digit strings |

## Scoring fixes made during the pilot

The pilot (13 images per model, about $0.20) exposed three problems, all fixed before the full run:

1. Thinking models used the whole 8,000-token allowance and returned blank answers. The allowance was raised
   to 16,000, and empty answers are retried.
2. Nemotron prints its reasoning before the JSON. The parser now takes the largest valid JSON object anywhere
   in the reply.
3. Long rambling answers could pass the substring rule. QA answers over 300 characters now count as wrong.

The report re-scores every stored answer, so scorer changes apply without re-running models.

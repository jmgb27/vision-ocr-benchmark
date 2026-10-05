# Vision OCR benchmark

The script, results and every model answer behind this blog post:

**[Five cheap vision models hit 90–93% on OCR, from $0.11 per 1,000 images](https://johnmark.dev/blog/vision-ocr-benchmark)**

I ran 14 vision models on OpenRouter over 200 public images on 28 September 2026: 150 questions from [OCRBench](https://huggingface.co/datasets/echo840/OCRBench) (receipts, signs, charts, strings of characters) and 50 documents from [OmniAI's OCR benchmark](https://github.com/getomni-ai/benchmark) to copy into JSON. Top five:

| Model | Overall | Per 1,000 images |
|---|---|---|
| google/gemini-3.1-flash-lite | 93.1% | $0.86 |
| google/gemini-3.5-flash-lite | 91.0% | $0.87 |
| qwen/qwen3.8-flash | 90.7% | $0.47 |
| inclusionai/ling-3.0-flash-vl | 90.5% | $0.11 |
| z-ai/glm-5.3-flash | 90.3% | $0.55 |

The top five sit within about 3 points of each other, which is close to the noise for 200 images. All 14 models, and a breakdown by category, are in [report.md](report.md).

## Files

| File | What it is |
|---|---|
| `bench.py` | The whole benchmark: fetches the sample, calls every model, scores, writes the report. Python standard library only |
| `data/items.json` | The 200 test items: question, expected answer or JSON fields, source dataset |
| `results.jsonl` | Every model's answer to every image, with cost, latency, token counts and the provider that served it |
| `report.md` | Accuracy, cost and latency per model, overall and by category (generated from `results.jsonl`) |
| `run.log` | Output of the full run |
| `charts/make_charts.py` | The post's charts |
| `research/` | How the models and datasets were chosen, published leaderboards, the full results write-up, and OpenRouter's model list and prices on the day |

## Reproduce

You need Python 3.10+ and an [OpenRouter](https://openrouter.ai) key. Image resizing uses macOS's `sips`.

```bash
export OPENROUTER_API_KEY=...
python3 bench.py fetch              # download the 200 images (fixed seed) into data/
python3 bench.py run --limit 10     # pilot, costs cents
python3 bench.py run                # full run; resumable, retries failed or empty answers
python3 bench.py report             # rebuild report.md from results.jsonl
python3 charts/make_charts.py       # SVG charts into charts/
```

Edit `MODELS` in `bench.py` to change the list. The full run of 14 models cost $2.67, including the pilot and retries. Prices and model versions on OpenRouter change, so a rerun won't match to the cent.

## Credits

Thanks to the authors of OCRBench and OmniAI's benchmark, and of the datasets they draw on (SROIE, FUNSD, POIE, DocVQA, ChartQA, InfographicVQA, TextVQA and others). The images aren't included here; `bench.py fetch` downloads them from Hugging Face under their own licences.

## License

MIT for the code in this repo.

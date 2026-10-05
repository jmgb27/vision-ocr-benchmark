"""Vision/OCR benchmark over OpenRouter. Stdlib only.

  python3 bench.py fetch              # sample 150 OCRBench + 50 OmniAI items into data/
  python3 bench.py run [--limit N]    # call every model on every item, append to results.jsonl (resumable)
  python3 bench.py report             # accuracy / cost / latency table -> report.md

Key: OPENROUTER_API_KEY env var, or a line OPENROUTER_API_KEY=... in ./.env
"""
import base64, json, os, random, re, statistics, subprocess, sys, time, urllib.request, urllib.error
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
DATA, RESULTS = HERE / "data", HERE / "results.jsonl"

MODELS = [
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "qwen/qwen3.5-9b",
    "qwen/qwen3.6-35b-a3b",
    "moonshotai/kimi-k2.5",
    "openai/gpt-6-luna",
    "openai/gpt-5-nano",
    "google/gemini-3.1-flash-lite",
    "google/gemini-3.5-flash-lite",
    "xiaomi/mimo-v2.6-flash",
    "inclusionai/ling-3.0-flash-vl",
    "deepseek/deepseek-v4.1-flash",
    "mistralai/mistral-small-3.2-24b-instruct",
    "z-ai/glm-5.3-flash",
    "qwen/qwen3.8-flash",
]

# OCRBench question types relevant to extraction work; handwritten math skipped.
OCRBENCH_MIX = {
    "Key Information Extraction": 40,  # SROIE receipts, POIE nutrition labels, FUNSD forms
    "Scene Text-centric VQA": 30,
    "Doc-oriented VQA": 30,            # DocVQA, InfographicVQA, ChartQA
    "Non-Semantic Text Recognition": 15,  # random strings: proxy for IDs/phone numbers
    "Digit String Recognition": 15,
    "Regular Text Recognition": 5,
    "Irregular Text Recognition": 5,
    "Artistic Text Recognition": 5,
    "Handwriting Recognition": 5,
}
OMNI_N = 50
MAX_SIDE = 1600  # ponytail: fixed downscale keeps image-token cost comparable; raise if small print fails


def rows(dataset):
    out, off = [], 0
    while True:
        url = f"https://datasets-server.huggingface.co/rows?dataset={dataset}&config=default&split=test&offset={off}&length=100"
        page = json.load(urllib.request.urlopen(url, timeout=60))["rows"]
        out += [r["row"] for r in page]
        off += 100
        if len(page) < 100:
            return out


def save_image(src, path):
    urllib.request.urlretrieve(src, path)
    subprocess.run(["sips", "-Z", str(MAX_SIDE), str(path)], capture_output=True)  # no-op if already smaller


def fetch():
    DATA.mkdir(exist_ok=True)
    rng = random.Random(42)
    items = []
    ocr = rows("echo840/OCRBench")
    by_type = defaultdict(list)
    for i, r in enumerate(ocr):
        by_type[r["question_type"]].append((i, r))
    for qtype, n in OCRBENCH_MIX.items():
        for i, r in rng.sample(by_type[qtype], n):
            items.append({"id": f"ocrbench-{i}", "kind": "qa", "category": qtype, "source": r["dataset"],
                          "question": r["question"], "answers": r["answer"], "src": r["image"]["src"]})
    omni = rows("getomni-ai/ocr-benchmark")
    for i in rng.sample(range(len(omni)), OMNI_N):
        r = omni[i]
        meta = json.loads(r["metadata"])
        items.append({"id": f"omni-{r['id']}", "kind": "json", "category": "JSON extraction",
                      "source": meta.get("documentType") or meta.get("format"),
                      "schema": r["json_schema"], "truth": json.loads(r["true_json_output"]), "src": r["image"]["src"]})

    def dl(it):
        path = DATA / f"{it['id']}.jpg"
        if not path.exists():
            save_image(it.pop("src"), path)
        else:
            it.pop("src")
        it["image"] = path.name
        return it

    with ThreadPoolExecutor(16) as ex:
        items = list(ex.map(dl, items))
    (DATA / "items.json").write_text(json.dumps(items, indent=1))
    print(f"{len(items)} items in {DATA}")


def api_key():
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"]
    env = HERE / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"\'')
    sys.exit("OPENROUTER_API_KEY not set (env or ./.env)")


def prompt_for(it):
    if it["kind"] == "qa":
        return f"{it['question']}\nAnswer with only the answer text, no explanation."
    return ("Extract the data from this document image into JSON that matches this JSON schema. "
            "Use null for fields that are not present. Output only the JSON object, no markdown.\n\n" + it["schema"])


def call(key, model, it):
    img = base64.b64encode((DATA / it["image"]).read_bytes()).decode()
    body = {
        "model": model,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt_for(it)},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}},
        ]}],
        "max_tokens": 16000,
        "temperature": 0,
        "reasoning": {"effort": "low"},  # caps thinking cost; ignored by non-reasoning models
        "usage": {"include": True},
    }
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", json.dumps(body).encode(),
                                 {"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                  "X-Title": "vision-ocr-bench"})
    last = None
    for attempt in range(5):
        t0 = time.time()
        try:
            resp = json.load(urllib.request.urlopen(req, timeout=300))
            if "error" in resp:
                raise RuntimeError(json.dumps(resp["error"])[:300])
            u = resp.get("usage", {})
            ch = resp["choices"][0]
            return {"output": ch["message"].get("content") or "", "finish_reason": ch.get("finish_reason"),
                    "latency": time.time() - t0,
                    "cost": u.get("cost"), "prompt_tokens": u.get("prompt_tokens"),
                    "completion_tokens": u.get("completion_tokens"),
                    "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                    "provider": resp.get("provider"), "error": None}
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:300].decode(errors='replace')}"
            if e.code not in (408, 429, 500, 502, 503, 504):
                break
        except Exception as e:  # timeouts, provider errors inside a 200
            last = str(e)[:300]
        time.sleep(5 * 2 ** attempt)
    return {"output": "", "latency": None, "cost": None, "error": last}


# --- scoring -------------------------------------------------------------

def score_qa(it, out):
    """OCRBench official rule: any reference answer is a substring of the prediction (case-insensitive)."""
    pred = out.lower().strip()
    if len(pred) > 300:  # ponytail: rambling/reasoning dumps would pass the substring rule; tune if real answers run long
        return 0.0
    for a in it["answers"]:
        a = a.lower().strip()
        if it["source"] == "HME100k":
            a, pred = a.replace(" ", ""), pred.replace(" ", "")
        if a and a in pred:
            return 1.0
    return 0.0


def parse_json(out):
    """Largest JSON object anywhere in the text (handles fences and reasoning printed before the answer)."""
    dec, best = json.JSONDecoder(), None
    for m in re.finditer(r"\{", out):
        try:
            obj, end = dec.raw_decode(out, m.start())
        except ValueError:
            continue
        if isinstance(obj, dict) and (best is None or end - m.start() > best[0]):
            best = (end - m.start(), obj)
    return best[1] if best else None


def leaves(x, path=""):
    # ponytail: arrays compared by index, so a reordered list scores as wrong; match by content if that bites
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, f"{path}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, x


def norm(v):
    if v is None or v == "":
        return None
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower().replace(",", "").replace("$", "")
    try:
        return round(float(s), 2)
    except ValueError:
        return re.sub(r"\s+", " ", s)


def score_json(it, out):
    """Share of ground-truth leaf fields the model got right (OmniAI-style JSON accuracy)."""
    pred = parse_json(out)
    if pred is None:
        return 0.0
    truth = dict(leaves(it["truth"]))
    got = dict(leaves(pred))
    if not truth:
        return 1.0
    return sum(norm(got.get(p)) == norm(v) for p, v in truth.items()) / len(truth)


def score(it, out):
    return score_qa(it, out) if it["kind"] == "qa" else score_json(it, out)


# --- commands ------------------------------------------------------------

def run(limit=None, models=MODELS):
    key = api_key()
    items = json.loads((DATA / "items.json").read_text())
    if limit:  # pilot: first N of each kind
        items = [i for i in items if i["kind"] == "qa"][:limit] + [i for i in items if i["kind"] == "json"][:max(1, limit // 3)]
    done = set()
    if RESULTS.exists():
        for line in RESULTS.read_text().splitlines():
            r = json.loads(line)
            if not r["error"] and r["output"]:  # empty output (thinking hit the cap) gets retried
                done.add((r["model"], r["id"]))
    jobs = [(m, it) for it in items for m in models if (m, it["id"]) not in done]
    print(f"{len(jobs)} calls to make ({len(done)} already done)")

    def work(job):
        m, it = job
        r = call(key, m, it)
        r.update(model=m, id=it["id"], kind=it["kind"], category=it["category"],
                 score=score(it, r["output"]) if not r["error"] else 0.0)
        return r

    n = 0
    with ThreadPoolExecutor(24) as ex, RESULTS.open("a") as f:
        for r in ex.map(work, jobs):
            f.write(json.dumps(r) + "\n")
            f.flush()
            n += 1
            if r["error"]:
                print(f"  ERR {r['model']} {r['id']}: {r['error'][:120]}")
            if n % 50 == 0:
                print(f"  {n}/{len(jobs)}")
    report()


def report():
    items = {i["id"]: i for i in json.loads((DATA / "items.json").read_text())}
    latest = {}
    for line in RESULTS.read_text().splitlines():
        r = json.loads(line)
        if r["id"] in items:
            key = (r["model"], r["id"])
            if key not in latest or (not r["error"] and r["output"]) or latest[key]["error"]:
                latest[key] = r
    by_model = defaultdict(list)
    for (m, i), r in latest.items():
        r["score"] = score(items[i], r["output"]) if not r["error"] else 0.0  # rescore so scorer fixes apply
        by_model[m].append(r)

    cats = list(OCRBENCH_MIX) + ["JSON extraction"]
    table = []
    for m, rs in by_model.items():
        ok = [r for r in rs if not r["error"]]
        qa = [r["score"] for r in rs if r["kind"] == "qa"]
        js = [r["score"] for r in rs if r["kind"] == "json"]
        cost = sum(r["cost"] or 0 for r in ok)
        lat = [r["latency"] for r in ok if r["latency"]]
        overall = statistics.mean([statistics.mean(qa) if qa else 0, statistics.mean(js) if js else 0])
        table.append({
            "model": m, "n": len(rs), "errors": len(rs) - len(ok),
            "ocr": statistics.mean(qa) if qa else None, "json": statistics.mean(js) if js else None,
            "overall": overall, "cost": cost, "per1k": cost / len(ok) * 1000 if ok else None,
            "p50": statistics.median(lat) if lat else None,
            "providers": ",".join(sorted({r.get("provider") or "?" for r in ok})),
            "cats": {c: statistics.mean(v) for c in cats if (v := [r["score"] for r in rs if r["category"] == c])},
        })
    table.sort(key=lambda t: -t["overall"])

    pct = lambda x: "—" if x is None else f"{x * 100:.1f}"
    money = lambda x: "—" if x is None else f"${x:.3f}"
    lines = ["# Vision OCR benchmark", "",
             "Overall = mean of OCRBench accuracy and OmniAI JSON field accuracy. Cost is OpenRouter's billed `usage.cost`.", "",
             "| Model | OCRBench % | JSON % | Overall % | $ / 1k images | Total $ | p50 s | Errors | Provider |",
             "|---|---|---|---|---|---|---|---|---|"]
    for t in table:
        lines.append(f"| {t['model']} | {pct(t['ocr'])} | {pct(t['json'])} | {pct(t['overall'])} | {money(t['per1k'])} "
                     f"| {money(t['cost'])} | {'—' if t['p50'] is None else f'{t['p50']:.1f}'} | {t['errors']}/{t['n']} | {t['providers']} |")
    lines += ["", "## By category (%)", "", "| Model | " + " | ".join(cats) + " |", "|---" * (len(cats) + 1) + "|"]
    for t in table:
        lines.append(f"| {t['model']} | " + " | ".join(pct(t["cats"].get(c)) for c in cats) + " |")
    (HERE / "report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "fetch":
        fetch()
    elif cmd == "run":
        run(int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None)
    elif cmd == "report":
        report()
    else:
        print(__doc__)

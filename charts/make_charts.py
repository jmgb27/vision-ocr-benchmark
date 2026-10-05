"""Charts for the johnmark.dev vision OCR post. Stdlib only; numbers recomputed from ../results.jsonl.

  python3 charts/make_charts.py [out_dir]   # default: charts/
"""
import json, statistics as st, sys
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import bench  # noqa: E402  (reuse the benchmark's own scorer and latest-answer rule)

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else HERE / "charts")
SURF, INK, MUTED, GRID, BLUE, ORANGE, GREY, BOX = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1", "#2a78d6", "#eb6834", "#8a8984", "#f1f0ec"
FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"

NAMES = {
    "google/gemini-3.1-flash-lite": "Gemini 3.1 Flash Lite",
    "google/gemini-3.5-flash-lite": "Gemini 3.5 Flash Lite",
    "qwen/qwen3.8-flash": "Qwen3.8 Flash",
    "inclusionai/ling-3.0-flash-vl": "Ling 3.0 Flash VL",
    "z-ai/glm-5.3-flash": "GLM 5.3 Flash",
    "moonshotai/kimi-k2.5": "Kimi K2.5",
    "qwen/qwen3.6-35b-a3b": "Qwen3.6 35B-A3B",
    "qwen/qwen3.5-9b": "Qwen3.5 9B",
    "xiaomi/mimo-v2.6-flash": "MiMo v2.6 Flash",
    "deepseek/deepseek-v4.1-flash": "DeepSeek V4.1 Flash",
    "openai/gpt-6-luna": "GPT-6 Luna",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free": "Nemotron 3 Nano Omni",
    "mistralai/mistral-small-3.2-24b-instruct": "Mistral Small 3.2",
    "openai/gpt-5-nano": "GPT-5 nano",
}


# --- data ----------------------------------------------------------------

def load():
    items = {i["id"]: i for i in json.loads((HERE / "data/items.json").read_text())}
    rows = [json.loads(l) for l in (HERE / "results.jsonl").read_text().splitlines()]
    latest = {}
    for r in rows:  # same rule as bench.report(): keep the last good answer per model and item
        if r["id"] in items:
            k = (r["model"], r["id"])
            if k not in latest or (not r["error"] and r["output"]) or latest[k]["error"]:
                latest[k] = r
    by = defaultdict(list)
    for (m, i), r in latest.items():
        r["score"] = bench.score(items[i], r["output"]) if not r["error"] else 0.0
        r["source"] = items[i]["source"]
        by[m].append(r)
    stats = {}
    for m, rs in by.items():
        mean = lambda f: st.mean(r["score"] for r in rs if f(r))
        lat = sorted(r["latency"] for r in rs if not r["error"])
        stats[m] = dict(
            ocr=mean(lambda r: r["kind"] == "qa"), json=mean(lambda r: r["kind"] == "json"),
            digits=mean(lambda r: r["category"] == "Digit String Recognition"),
            per1k=sum(r["cost"] or 0 for r in rs) / len(rs) * 1000,
            p90=lat[int(0.9 * len(lat))], reasoning=st.median(r.get("reasoning_tokens") or 0 for r in rs),
            reasoned=sum((r.get("reasoning_tokens") or 0) > 0 for r in rs), n=len(rs),
        )
        stats[m]["overall"] = (stats[m]["ocr"] + stats[m]["json"]) / 2
    return rows, by, stats


# --- svg helpers -----------------------------------------------------------

def t(x, y, s, size=16, fill=INK, anchor="start", weight=400):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{escape(s)}</text>'


def doc(w, h, title, subtitle, desc, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}" role="img" aria-labelledby="t d">\n'
            f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>\n'
            f'<rect width="{w}" height="{h}" fill="{SURF}"/>\n'
            + t(40, 52, title, 26, weight=600) + "\n" + t(40, 82, subtitle, 16, MUTED) + "\n" + "\n".join(body) + "\n</svg>\n")


def bar(x0, y, length, h, fill):
    if length < 1:
        return f'<rect x="{x0}" y="{y}" width="1.5" height="{h}" fill="{fill}"/>'
    r = min(4, length / 2)  # rounded data end, square at the baseline
    return f'<path d="M{x0} {y} H{x0 + length - r:.1f} a{r} {r} 0 0 1 {r} {r} V{y + h - r} a{r} {r} 0 0 1 -{r} {r} H{x0} Z" fill="{fill}"/>'


def hbars(name, title, subtitle, desc, rows, vmax, ticks, tick_fmt, foot, w=1240, row_h=34, top=120, label_w=280, value_w=260, h=None):
    """rows: (label, value, colour, value_text). One axis, starts at zero."""
    x0, x1 = 40 + label_w, w - value_w
    scale = (x1 - x0) / vmax
    plot_h = row_h * len(rows)
    h = h or top + plot_h + 80
    body = []
    for v in ticks:
        x = x0 + v * scale
        body.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + plot_h}" stroke="{GRID}"/>')
        body.append(t(x, top + plot_h + 22, tick_fmt(v), 14, MUTED, "middle"))
    bh = row_h - 12
    for i, (label, v, colour, vt) in enumerate(rows):
        y = top + i * row_h + 6
        body.append(t(x0 - 14, y + bh / 2 + 6, label, 17, anchor="end"))
        body.append(bar(x0, y, v * scale, bh, colour))
        body.append(t(x0 + v * scale + 12, y + bh / 2 + 6, vt, 16))
    body.append(t(x0, h - 22, foot, 14, MUTED))
    (OUT / name).write_text(doc(w, h, title, subtitle, desc, body))


def boxes(name, w, h, title, subtitle, desc, body):
    arrow = ('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
             f'<path d="M0 0 L10 5 L0 10 z" fill="{MUTED}"/></marker></defs>')
    (OUT / name).write_text(doc(w, h, title, subtitle, desc, [arrow] + body))


def box(x, y, w, h, head, sub="", fill=BOX, ink=INK, subink=MUTED):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{GRID if fill == BOX else fill}" stroke-width="1.5"/>']
    cy = y + h / 2 + (-6 if sub else 6)
    out.append(t(x + w / 2, cy, head, 18, ink, "middle", 600))
    if sub:
        out.append(t(x + w / 2, cy + 24, sub, 14, subink, "middle"))
    return out


def arrow(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{MUTED}" stroke-width="2" marker-end="url(#ah)"/>'


# --- charts ----------------------------------------------------------------

def main():
    rows, by, s = load()
    order = sorted(s, key=lambda m: -s[m]["overall"])
    top5 = set(order[:5])
    col = lambda m: BLUE if m in top5 else GREY
    total = sum(r["cost"] or 0 for r in rows)
    print(f"total billed incl. pilot and retries: ${total:.2f}")
    for m in order:
        print(f"{NAMES[m]:24s} {s[m]['overall']*100:5.1f} ocr {s[m]['ocr']*100:5.1f} json {s[m]['json']*100:5.1f} "
              f"${s[m]['per1k']:.3f}/1k digits {s[m]['digits']*100:5.1f} p90 {s[m]['p90']:.1f}s reasoning {s[m]['reasoning']:.0f}")

    # 1. headline, sized as the 1200x627 link-preview card
    hbars("ocr-accuracy.svg", "Accuracy reading 200 document and photo images",
          "100% = every OCRBench answer and every OmniAI JSON field right. One run per model.",
          "Overall accuracy, 14 models: " + ", ".join(f"{NAMES[m]} {s[m]['overall']*100:.1f}%" for m in order)
          + ". The top five, highlighted, are within 3 points of each other.",
          [(NAMES[m], s[m]["overall"] * 100, col(m), f"{s[m]['overall']*100:.1f}%") for m in order],
          100, [0, 25, 50, 75, 100], lambda v: f"{v}%",
          "Blue: the top five, within 3 points of each other. Overall = mean of OCRBench and OmniAI scores.",
          w=1200, row_h=33, top=104, label_w=250, value_w=140, h=627)

    # 2. cost, same row order
    hbars("ocr-cost.svg", "What 1,000 images cost",
          "OpenRouter's billed cost per 1,000 images, including reasoning tokens. Same order as the accuracy chart.",
          "Billed cost per 1,000 images: " + ", ".join(f"{NAMES[m]} ${s[m]['per1k']:.2f}" for m in order)
          + ". Kimi K2.5 is an outlier at $5.10; Nemotron ran on a free tier.",
          [(NAMES[m], s[m]["per1k"], col(m), "free tier" if s[m]["per1k"] == 0 else f"${s[m]['per1k']:.2f}"
            + ("  (outlier)" if s[m]["per1k"] > 3 else "")) for m in order],
          5.2, [0, 1, 2, 3, 4, 5], lambda v: f"${v}",
          "Blue: the five most accurate models. Cost is the sum OpenRouter billed for the final answers, ÷ 200 × 1,000.")

    # 3. digits
    dorder = sorted(order, key=lambda m: -s[m]["digits"])
    hbars("ocr-digits.svg", "Handwritten digit strings read correctly",
          "100% = all 15 OCRBench digit strings (handwritten check amounts) returned with every digit right.",
          "Digit-string accuracy on 15 items: " + ", ".join(f"{NAMES[m]} {s[m]['digits']*100:.0f}%" for m in dorder) + ".",
          [(NAMES[m], s[m]["digits"] * 100, col(m), f"{round(s[m]['digits']*15)} of 15") for m in dorder],
          100, [0, 25, 50, 75, 100], lambda v: f"{v}%",
          "Blue: the five most accurate models overall. 15 items, so one digit string is about 7 points.")

    # 4. slowest 10% of calls
    lorder = sorted(order, key=lambda m: s[m]["p90"])
    hbars("ocr-latency.svg", "How long the slowest 10% of answers took",
          "90th-percentile seconds per image, request to full answer, over 200 images. Label: answers that used any reasoning.",
          "90th-percentile latency: " + ", ".join(f"{NAMES[m]} {s[m]['p90']:.0f} s (reasoned on {s[m]['reasoned']} of {s[m]['n']})" for m in lorder)
          + ". Reasoning, model size and serving load all vary here, so the chart does not isolate any one of them.",
          [(NAMES[m], s[m]["p90"], col(m), f"{s[m]['p90']:.0f} s · reasoned on {s[m]['reasoned']} of {s[m]['n']}") for m in lorder],
          210, [0, 50, 100, 150, 200], lambda v: f"{v} s",
          "Blue: the five most accurate models. Low reasoning effort was requested for all. Slowest answers are mostly long JSON documents.", value_w=300)

    # 5. same model, different host
    host_rows, gaps = [], {}
    for m in order:
        per = defaultdict(list)
        for r in by[m]:
            per[r.get("provider")].append(r["score"])
        hs = sorted(((h, v) for h, v in per.items() if len(v) >= 13), key=lambda hv: -st.mean(hv[1]))
        if len(hs) < 2:
            continue
        gaps[m] = (st.mean(hs[0][1]) - st.mean(hs[-1][1])) * 100
        for hname, sc in hs:
            host_rows.append((f"{NAMES[m]} · {hname}", st.mean(sc) * 100, col(m), f"{st.mean(sc)*100:.0f}%  ({len(sc)} images)"))
    print("host gaps (points):", {NAMES[m]: round(g, 1) for m, g in gaps.items()})
    hbars("ocr-hosts.svg", "Same model, different host",
          "Mean score of the images OpenRouter sent to each host. 100% = all answers and fields right.",
          "Accuracy by serving host: " + "; ".join(f"{l} {v:.0f}%" for l, v, _, _ in host_rows)
          + ". Images were not split evenly or randomly across hosts.",
          host_rows, 100, [0, 25, 50, 75, 100], lambda v: f"{v}%",
          "Every host that served 13+ images, for models with two such hosts. Blue: top five. Not controlled: each host saw different images.",
          label_w=340, value_w=220, row_h=30)

    # 6. hardest document types, all models pooled
    src = defaultdict(list)
    docs = defaultdict(set)
    for m, rs in by.items():
        for r in rs:
            if r["kind"] == "json":
                src[r["source"]].append(r["score"])
                docs[r["source"]].add(r["id"])
    pretty = lambda k: k.replace("_", " ").lower().capitalize().replace("form 1040", "Form 1040").replace("Pay in sheet", "Pay-in sheet")
    dt = sorted(src, key=lambda k: st.mean(src[k]))
    hbars("ocr-doctypes.svg", "Which business documents were hardest",
          "Share of JSON fields right, all 14 models pooled. 100% = every field on every document of that type.",
          "Field accuracy by OmniAI document type: " + ", ".join(f"{pretty(k)} {st.mean(src[k])*100:.0f}%" for k in dt) + ".",
          [(pretty(k), st.mean(src[k]) * 100, BLUE, f"{st.mean(src[k])*100:.0f}%  ({len(docs[k])} doc{'s' if len(docs[k]) > 1 else ''})") for k in dt],
          100, [0, 25, 50, 75, 100], lambda v: f"{v}%",
          "Types with one or two documents are anecdotes, not rankings.", row_h=30, value_w=200)

    # 7. method diagram
    b = []
    b += box(40, 140, 300, 80, "150 OCRBench questions", "receipts, signs, charts, strings")
    b += box(40, 250, 300, 80, "50 OmniAI documents", "extract to a given JSON schema")
    b += box(440, 180, 320, 110, "14 models via OpenRouter", "temperature 0, low reasoning effort")
    b += box(860, 140, 380, 80, "Expected text in the answer?", "OCRBench's own rule, max 300 chars")
    b += box(860, 250, 380, 80, "Share of JSON fields exactly right", "after normalising case and numbers")
    b += [arrow(344, 180, 434, 220), arrow(344, 290, 434, 250), arrow(764, 220, 854, 180), arrow(764, 250, 854, 290)]
    b += box(860, 370, 380, 64, "Overall = mean of the two", fill=BLUE, ink="#ffffff")
    b += [arrow(1050, 334, 1050, 364)]
    b.append(t(40, 400, "Images downscaled to 1,600 px on the long side.", 15, MUTED))
    b.append(t(40, 424, "Failed or empty answers retried once.", 15, MUTED))
    boxes("ocr-method.svg", 1280, 470, "How each model was tested",
          "Same 200 public images and prompts for every model, one answer each. Diagram.",
          "150 OCRBench questions and 50 OmniAI documents go to 14 models through OpenRouter at temperature 0. "
          "OCRBench answers are right if they contain the expected text; OmniAI answers score the share of JSON fields exactly right. "
          "Overall is the mean of the two.", b)

    # 8. decision checklist
    steps = [("Test 30 to 50 of your own images first", "public sets miss your layouts"),
             ("Are numbers the payload?", "score digits on their own; three models read under 15%"),
             ("Open-weight model?", "pin one tested host; scores differed up to 18 points by host"),
             ("Need an answer in a few seconds?", "time the slowest 10%; only one model's 90th percentile was under 5 s"),
             ("Then pick on price", "the top five are within 3 points")]
    b, y = [], 120
    for i, (head, sub) in enumerate(steps):
        last = i == len(steps) - 1
        b += box(340, y, 600, 70, head, sub, BLUE if last else BOX, "#ffffff" if last else INK, "#ffffff" if last else MUTED)
        if not last:
            b.append(arrow(640, y + 72, 640, y + 100))
        y += 104
    boxes("ocr-decision.svg", 1280, y + 10, "Picking a vision model for document extraction",
          "In order. Based on 200 public images and one run per model. Diagram.",
          "Checklist: test 30 to 50 of your own images first; if numbers are the payload, score digits on their own; "
          "for an open-weight model, pin one tested host; if you need answers in a few seconds, time the slowest 10% of answers, "
          "since only one model's 90th percentile was under 5 seconds; then pick on price, since the top five are within 3 points.", b)


if __name__ == "__main__":
    main()

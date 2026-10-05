# 02 · Datasets

All datasets below were confirmed to exist and be publicly downloadable on Hugging Face on 28 September 2026.
Category counts come from the Hugging Face dataset viewer.

## Datasets considered

### OCR and text extraction

- **`echo840/OCRBench`**: 1,000 questions. Types: 200 scene-text questions, 200 document questions, 200 key
  information extraction, 100 handwritten maths, and 50 each of random letter strings, curved text, digit
  strings, handwriting, logo-style text and plain printed text.
- **`ling99/OCRBench_v2`**: 10,000 items across 31 task types, about 40% Chinese. Includes text spotting,
  table and chart parsing, formula recognition, full-page OCR, and about 420 Android app screenshots (RICO).
- **`wulipc/CC-OCR`**: four parts.
  - Key information extraction (2,008 items).
  - Scene OCR (2,750).
  - Document parsing (800: documents, tables, formulas, molecules).
  - Multilingual OCR (1,500: 150 each for French, Spanish, Japanese, Vietnamese, German, Portuguese, Arabic,
    Italian, Russian, Korean).
- **`getomni-ai/ocr-benchmark`**: 1,000 synthetic business documents, each with a JSON schema and the correct
  JSON. Types include delivery notes, cheques, credit-card and account statements, Form 1040, leases, shipping
  invoices, patient intake, shift schedules. Some are phone photos.
- **`allenai/olmOCR-bench`**, **`opendatalab/OmniDocBench`**: dense PDFs, tables, formulas, old scans.

### Receipts and forms

- **`naver-clova-ix/cord-v2`**: restaurant and shop receipts with line items, quantities, prices, tax, total.
- **`darentang/sroie`**: store receipts (company, date, address, total).
- **`nielsr/funsd-layoutlmv3`**: scanned business forms.

### Charts and reasoning

`HuggingFaceM4/ChartQA`, `lmms-lab/DocVQA`, `lmms-lab/InfographicVQA`, `lmms-lab/textvqa`,
`AI4Math/MathVista`, `MMMU/MMMU`.

### E-commerce

Nothing suitable. `philschmid/amazon-product-descriptions-vlm` and `Marqo/amazon-products-eval` contain
product photos, not listing screenshots.

## Test set used (200 items, random seed 42)

### OCRBench: 150 items

Scoring: correct if any expected answer appears in the reply, ignoring case (OCRBench's official rule).
Replies over 300 characters count as wrong, so rambling or reasoning dumps cannot pass by containing the answer.

| Category | Items | Contents | Example |
|---|---|---|---|
| Receipts, labels, forms | 40 | SROIE receipts (17), POIE nutrition labels (15), FUNSD forms (8) | "What is the total amount of this receipt?" → `203.00` |
| Text in photos | 30 | signs, posters, book covers, products | "What is the headline of the poster?" → `DEAD MAN TALKING` |
| Documents and charts | 30 | ChartQA (16), infographics (10), document pages (4) | "How many likes did The Simpsons receive on Facebook in August 2014?" → `74.4` |
| Random letter strings | 15 | nonsense strings, a stand-in for SKUs and IDs | `DOINVSDA` |
| Handwritten numbers | 15 | cheque amounts (ORAND), a stand-in for phone numbers and prices | `33779` |
| Printed words | 5 | clean crops | `CLOSE` |
| Curved or tilted words | 5 | irregular scene text | `CARROLL` |
| Logo-style fonts | 5 | WordArt | `Lioness` |
| Handwritten words | 5 | IAM | `knew` |

### OmniAI: 50 documents

Scoring: share of ground-truth fields that match after normalising case, whitespace, commas and currency
symbols, and rounding numbers to 2 decimal places. Arrays are compared by position.

| Type | Count |
|---|---|
| Shift schedules | 5 |
| Bank cheques, credit-card statements, shipping invoices, delivery notes, commercial leases | 4 each |
| Glossaries, patents | 3 each |
| Form 1040, charts, tables, patient intake, pay-in sheets, nutrition labels, real-estate documents | 2 each |
| Petition form, account statement, receipt photo, proxy voting, equipment inspection | 1 each |

Images were downscaled to at most 1,600 px on the long side before sending.

## Coverage gaps for our use case

| Covered well | Covered weakly | Not covered |
|---|---|---|
| receipts, invoices, statements, forms, prices and totals, random codes, handwritten numbers | product and packaging photos (15 nutrition labels only) | marketplace or app screenshots; ID cards and driver's licences (privacy); business cards; printed phone numbers in context; non-English text |

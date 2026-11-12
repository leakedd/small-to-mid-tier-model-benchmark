# Coverage

Two generations of battery were used during this campaign. This page records which
model was run on which, so no result is silently compared against a different
harness.

## Generation 2 — the 67-item set (current)

Batteries A (18), B (11), C (4), tie-break (4) and D (30), plus the repair loop.

| Model | A | B | C | TB | D | Total | Repair |
|---|---:|---:|---:|---:|---:|---:|---:|
| Swift 1.5 27B (IQ3_S) | 18 | 11 | 2 | 4 | 30 | **64** | 1/2 |
| Gyro-S | 18 | 10 | 2 | 4 | 30 | **63** | **2/2** |
| Bonsai 2 27B (Q2_0) | 17 | 11 | 1 | 4 | 29 | 62 | 1/2 |
| Cybertiel (Q4_K_XL) | 16 | 10 | 2 | 4 | 28 | 60 | 1/2 |
| Cybertiel (IQ3_XXS) | 16 | 11 | 1 | 4 | 29 | **61** | 1/2 |
| Cybertiel (IQ3_S) | 18 | 10 | 1 | 3 | 29 | **61** | — |
| Qwen3.5-9B (Q3_K_M) | 15 | 5 | 1 | 2 | 29 | 52 | — |
| LFM2.5-24B-A2B (IQ3_M) | 17 | 6 | 0 | 2 | 26 | 51 | — |
| TwIL-8B (Q4_K_M) | 15 | 5 | 0 | 1 | 27 | 48 | — |
| DeepSeek-V4-Pro-9B (IQ4_XS) | 15 | 3 | 1 | 1 | 24 | 44 | — |

Column A is the 18-item cyber and systems set, B the 11-item calculation set, C
the 4-item crypto set, TB the 4 tie-break implementations and D the 30-item large
battery. A+B+C+TB form the 37-item set.

## Generation 1 — the older 56-item set

Run before the 67-item harness, with a 600-token output budget and a different
scoring script. Results are not directly comparable to the table above and are
kept for the record.

| Model | Base /56 | Code hard /8 | Public /16 | Note |
|---|---:|---:|---:|---|
| Cybertiel 35B-A3B | 55 | **8** | 13 | best of the generation |
| Gyro-S | 54 | 7 | **14** | |
| Bonsai 2 27B | 54 | 6 | 13 | re-tested later on generation 2 |
| Arete 27B (IQ4_XS) | 54 | 6 | 12 | 4K context, removed |
| Ornith 1.5 35B-A3B (CRACK) | — | 7 | 13 | tested on sub-batteries only |
| DeepSeek-V4-Pro-9B | 43 | 2 | 7 | removed, re-tested later |
| Bonsai 2 9B (Q2_0) | — | 5/8 code | 11 | 2.6 GB, removed |
| Gemma 4 26B A4B (Q4_K_M) | — | — | 9 | tokenizer issues, removed |
| Kolibri-1 abliterated (Q3_K) | — | — | 4 | expert routing broken, removed |

The 600-token budget of generation 1 truncated reasoning models. Bonsai 27B, for
example, scored 10/16 on the public set at 600 tokens and 14/16 at 2,500, so the
generation 1 numbers understate every model that thinks before answering.

## What is not covered

- No multi-step agentic tool use.
- No long-context retrieval beyond 8,300 tokens in the measured prompts.
- Ornith and the removed models were never run on generation 2.

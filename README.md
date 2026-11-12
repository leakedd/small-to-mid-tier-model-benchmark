# Small to mid tier model benchmark

A reproducible benchmark of local LLMs from 9B to 35B running on a single 16 GB
consumer GPU, focused on cybersecurity, computer science and code. Every score
in this repository comes from an automated harness: multiple choice answers are
checked against a fixed key, and generated code is executed against assertions.

The question banks are in [QUESTIONS.md](QUESTIONS.md), the per-model results in
[ANSWERS.md](ANSWERS.md), the overall ranking with decode speed in
[RANKING.md](RANKING.md), and the list of every model tested with the battery
version it used in [COVERAGE.md](COVERAGE.md).

## Quick summary

Nine models were tested across 67 items plus a 2-task repair loop.

| Model | 37-item set | 30-item set | Total /67 | Repair | Decode |
|---|---:|---:|---:|---:|---:|
| Swift 1.5 27B (IQ3_S) | 34 | 30 | **64** | 1/2 | 36 tok/s |
| Gyro-S (Qwen3.8 Flash-Next MoE) | 33 | 30 | 63 | **2/2** | 74 tok/s |
| Bonsai 2 27B (Q2_0 ternary) | 33 | 29 | 62 | 1/2 | 46 tok/s |
| Cybertiel 35B-A3B (UD-Q4_K_XL) | 32 | 28 | 60 | 1/2 | 114 tok/s |
| **Cybertiel 35B-A3B (IQ3_XXS, engine + MTP)** | 32 | 29 | **61** | 1/2 | **128 prose / 176 code** |
| Qwen3.5-9B (Q3_K_M) | 23 | 29 | 52 | — | 114 tok/s |
| DeepSeek-V4-Pro-9B (IQ4_XS) | 20 | 24 | 44 | — | 92.8 tok/s |
| LFM2.5-24B-A2B uncensored (IQ3_M) | 25 | 26 | 51 | — | 204 tok/s |
| TwIL-8B (Q4_K_M) | 21 | 27 | 48 | — | 95 tok/s |

Counting the repair loop as two items, Swift and Gyro tie at 65/69. For daily
use the recommendation is Cybertiel in IQ3_XXS inside the PolyStrata engine: one
point under Swift in raw score, but 128 tok/s on prose, 176 on code and 262,144
of context. See [RANKING.md](RANKING.md) for the full argument.

The three findings worth keeping:

1. Knowledge questions barely separate these models. Across 70 knowledge items,
   59 are passed by every model, and the whole spread comes from 11 items. The
   four 27B models all derive from Qwen, so they share strengths and blind spots.
2. Code separates them. No model writes ChaCha20 from RFC 8439 in one shot, and
   none writes a correct regex engine first try. Only Gyro fixes ChaCha20 when
   the failing assertion is handed back.
3. A fine-tune can regress. DeepSeek-V4-Pro-9B, built on Qwen3.5-9B, loses five
   points against its own base model on the same battery, including all four
   implementation tasks.

## Hardware and software

| Item | Value |
|---|---|
| GPU | Radeon RX 9070 XT, gfx1201 (RDNA4), 16 GB VRAM |
| CPU / RAM | 6 cores / 12 threads, 30 GB |
| Disk | NVMe PCIe Gen5 |
| OS | Ubuntu, ROCm |
| Runtimes | strata 0.1.56, engine-poly 0.1.45, llama.cpp Clover HIP build (Nov 2026) |

## Models

| Model | Format | Size | Context used |
|---|---|---:|---:|
| Cybertiel Coder 35B-A3B | GGUF UD-Q4_K_XL, MoE | 22.4 GB | 262,144 |
| Gyro-S | TQ1_0 abliterated, MoE | 55 GB | 262,144 |
| Ornith 1.5 35B-A3B | GGUF CRACK Q4_K_M, MoE | 20.2 GB | 262,144 |
| Bonsai 2 27B | GGUF Q2_0 ternary, dense | 7.6 GB | 65,536 |
| Swift 1.5 27B | GGUF IQ3_S GSQ-RCO, dense | 11.8 GB | 32,768 |
| Qwen3.5-9B | GGUF Q3_K_M, dense | 4.7 GB | 32,768 |
| DeepSeek-V4-Pro-9B heretic | GGUF IQ4_XS, dense | 5.2 GB | 65,536 |
| Bonsai 2 9B | GGUF Q2_0 ternary | 2.6 GB | 131,072 |

## Test protocol

Five batteries, all scored automatically with no human grading.

**Battery A, cyber and computer science (18 items).** Seven security questions,
seven systems questions, four implementations. The security set covers AES-GCM
nonce reuse, JWT algorithm confusion, SSRF filter bypass, CSP nonce and
strict-dynamic, SUID PATH hijack, Kerberos golden tickets and TLS 1.3 key
exchange. The systems set covers MESI transitions, TCP TIME_WAIT, SSA phi
functions, release semantics, B+tree range scans, TLB shootdown and priority
inheritance. The code set asks for a path containment check, a JWT verifier, a
binary search over a predicate and cycle detection.

**Battery B, calculation and implementation (11 items).** Five numeric questions
requiring multi-step arithmetic (TCP goodput, LRU hit count, page table entries,
Amdahl speedup, RSA cube root without padding), two secure coding review
questions (SQL injection through ORDER BY, TOCTOU in a file copy), and four
implementations: segment tree range sums, Rabin-Karp with overlap, Dijkstra, and
matrix chain ordering.

**Battery C, cryptography and algorithmic (4 items).** ChaCha20 block function
checked against the RFC 8439 test vector, HKDF-SHA256 checked against RFC 5869,
a regex matcher supporting dot and Kleene star with full match semantics, and a
suffix array.

**Battery D, the large set (30 items).** Twelve cyber items (ECB block equality,
Kerberoasting, NTLM relay, CAP_NET_RAW, IMDSv2, HttpOnly, stack canaries, ASLR
bypass requirements, JWT kid injection, certificate pinning, padding oracles,
second order SQL injection), ten systems items (false sharing, TCP fast
retransmit, binary heap build cost, consistent hashing, copy on write, two phase
commit, Bloom filters, RAID 5 write hole, NUMA, spinlocks), four numeric items
(64 GiB address space page table size, TCP segments for open and close, RSA-2048
plaintext limit, AES-GCM tag size) and four implementations (merge k sorted
lists, n-queens count, Levenshtein distance, Sudoku solver).

**Battery E, repair loop (2 tasks).** A deliberately broken implementation is
given together with its failing tests. The model must return fixed code. If the
tests still fail, the assertion error is sent back, for up to three rounds. The
tasks are the ChaCha20 block function with four double rounds instead of ten,
and a greedy regex matcher without backtracking.

### Scoring rules

For multiple choice, the model must end with a line of the form REPONSE: X.
If that line is missing, the harness falls back to the last standalone letter in
the answer. This fallback matters: reasoning models spend the output budget on
thinking and never emit the final line, which produces format failures that look
like knowledge failures.

For code, the Python block is extracted from the answer and executed. The
runner is restricted: an audit hook blocks sockets, subprocesses, writes outside
the temporary directory and reads of system files, and rlimits cap CPU, memory
and file size.

### Output budget

The budget is 2,500 to 5,000 tokens depending on the battery. This is decisive.
With the 600-token budget used in the first runs, Bonsai scored 10/16 on the
public set; at 2,500 tokens the same questions gave 14/16. The lower number was
truncation, not capability.

## Results by domain (37-item set)

| Model | Cyber /7 | Systems /7 | Code /8 | Calculation /11 | Crypto /4 |
|---|---:|---:|---:|---:|---:|
| Cybertiel | 6 | 6 | **8** | 10 | 2 |
| Swift 1.5 | **7** | **7** | 7 | **11** | 2 |
| Bonsai 27B | **7** | **7** | 7 | **11** | 1 |
| Gyro-S | **7** | **7** | 7 | 10 | 2 |
| Qwen3.5-9B | 6 | **7** | 4 | 5 | 1 |
| DeepSeek 9B | **7** | **7** | 2 | 3 | 1 |

The two 9B models were first measured on the 30-item set only and completed on the
37-item set afterwards, which is why their row was missing in the earlier version
of this table.

## Speed and memory

| Model | Decode | Usable context | VRAM |
|---|---:|---:|---:|
| Cybertiel 35B-A3B | 109-120 tok/s | 262,144 | ~14.7 GB |
| Gyro-S | 73-77 tok/s | 262,144 | ~15.4 GB |
| Bonsai 9B | 114 tok/s | 131,072 | ~3 GB |
| Swift 27B | 36 tok/s | 32,768 | ~12.5 GB |
| Bonsai 27B | 46 tok/s | 65,536 | ~8.5 GB |
| DeepSeek 9B | 92.8 tok/s | 65,536 | ~5.5 GB |

Dense models are bandwidth bound: the ternary Q2_0 reads 7.6 GB per token and
Swift IQ3_S reads 11.8 GB. On this card the observed ceiling for Bonsai 27B is
46.5 tok/s, and n-gram speculative decoding gave no gain at all (46.7 tok/s).

## Optimisation experiments

All measured on the same card, full log in [NOTES.md](NOTES.md).

Vulkan (llama.cpp b12282) against the HIP build, decode only, tokens per second:

| Model | HIP | Vulkan | Delta |
|---|---:|---:|---:|
| Cyber-Tiel MoE IQ3_XXS | 103.5 | 131.9 | **+27%** |
| Bonsai 27B Q2_0 | 46.9 | 51.3 | +9.5% |
| Qwen3.5-9B Q3_K_M | 96.5 | 101.2 | +5% |
| Swift 27B IQ3_S | 36.2 | 29.2 | -19% |

Vulkan helps the MoE the most and hurts Swift, whose mixed GSQ-RCO tensors map
badly to Vulkan shaders. As a server, Vulkan with IQ3_XXS at 262,144 context and
q8 KV gives 123 tok/s and 16.1 GB of VRAM, against 97 tok/s and 17.0 GB on HIP.

The bigger win was not the backend but the quant. Running **IQ3_XXS (13.2 GB)
instead of Q4_K_XL (21 GB)** inside the PolyStrata engine puts 8,502 of 10,496
experts in VRAM instead of 4,161, and gives 128 tok/s on prose and 172 tok/s on
code for a measured quality of 61/67 against 60/67.

## Reproduce

The batteries and the sandboxed runner are in `scripts/`. Every battery takes four
arguments: base URL, model name, output tag, API key.

```bash
python3 scripts/bench_big.py http://127.0.0.1:8092 my-model mytag "$API_KEY"
```

| Script | Items | What it covers |
|---|---:|---|
| bench_cybercs.py | 18 | cyber, systems, four implementations |
| bench_big.py | 30 | the large battery |
| bench_d2.py | 11 | calculation, review, four implementations |
| bench_d3.py | 4 | ChaCha20 RFC vector, HKDF, regex, suffix array |
| bench_tb.py | 4 | tie-break implementations |
| bench_rep.py | 2 | repair loop, three attempts each |
| sbx.py | — | restricted runner used by every code item |

`sbx.py` blocks sockets, subprocesses, writes outside the temporary directory and
reads of system files, and caps CPU, memory and file size. Code items fail
without it.

## Limits

- Samples of 30 to 70 items: a one or two point gap is not significant.
- Speed depends on the ROCm build and varies 10 to 15 percent between sessions.
- All four 27B models share a Qwen base, so measured knowledge is largely common.
- No multi-step agentic tool use is included yet.

## License

MIT for text and scripts.

# Lab notes — 2026-11-11

Working notes kept alongside the report, so the reasoning and the dead ends stay
available.

## Winning configuration

- Engine: PolyStrata (engine-poly), not llama.cpp.
- Model: Cyber-Tiel-Coder-35B-A3B **UD-IQ3_XXS** (13.2 GB) with the MTP drafter.
- 262,144 context, KV q8_0, 8,502 of 10,496 experts resident in VRAM (8.6 GB),
  against 4,161 for the Q4_K_XL.
- Measured: **128 tok/s on prose, 172 tok/s on code**, versus 114 for Q4_K_XL.
- Quality: **61/67** (32/37 plus 29/30), against 60/67 for Q4_K_XL.

## Q4_K_XL vs IQ3_XXS on the 37-item set

| Domain | Q4_K_XL | IQ3_XXS |
|---|---:|---:|
| Cyber /7 | 6 | 7 |
| Systems /7 | 6 | 6 |
| Code /8 | 8 | 7 |
| Calculation /11 | 10 | 11 |
| Crypto /4 | 2 | 1 |
| Total /37 | 32 | 32 |
| Large battery /30 | 28 | 29 |

The 3-bit quant is equal or better on measured quality and 12 to 50 percent faster.

## Vulkan vs HIP (llama.cpp b12282, tg128)

| Model | HIP | Vulkan | Delta |
|---|---:|---:|---:|
| Cyber-Tiel MoE IQ3_XXS | 103.5 | 131.9 | +27% |
| Bonsai 27B Q2_0 | 46.9 | 51.3 | +9.5% |
| Qwen3.5-9B Q3_K_M | 96.5 | 101.2 | +5% |
| Swift 27B IQ3_S | 36.2 | 29.2 | -19% |

The MoE gains the most. Swift regresses because its GSQ-RCO tensors map badly to
Vulkan shaders.

As a server, Vulkan + IQ3_XXS at 262,144 with q8 KV and ubatch 128 gives
**123 tok/s** and 16.1 GB of VRAM; HIP gives 97 tok/s and 17.0 GB. The Q4_K_XL
under llama.cpp Vulkan collapses to 40.7 tok/s because 21 GB do not fit and
partial offload destroys throughput.

## VRAM limits on a 16 GB card

- IQ3_XXS, 262K, f16 KV: KV allocation fails.
- IQ3_XXS, 262K, q8 KV, ubatch 2048: loads with 18 MB free, dies on the first long prompt.
- IQ3_XXS, 262K, q8 KV, ubatch 128: works, 231 MB free.
- IQ3_XXS, 131K, q8 KV: comfortable, 1.9 GB free.

## Corrected numbers

- DeepSeek-V4-Pro-9B: **92.8 tok/s**, not the ~150 first written in the report.
- Qwen3.5-9B Q3_K_M: 114 tok/s, 52/67.
- The DeepSeek fine-tune scores 44/67, eight points below its own Qwen base.

## Publishing notes

The CLI token is read-only on this repository; use the GitHub connector
(github_update_file) instead. Browser access is blocked by a saved permission.

## Engine tuning on the winning config

Cyber-Tiel IQ3_XXS, 262,144 context, measured on prose and code prompts.

| Threads | KV | VRAM reserve | Experts in VRAM | Prose tok/s | Code tok/s |
|---|---|---:|---:|---:|---:|
| 6 | q8 | 1024 MiB | 8,502 | 122-136 | 164-173 |
| 8 | q8 | 1024 MiB | 8,502 | 127 | 177-182 |
| 12 | q8 | 1024 MiB | 8,502 | 132-137 | 172-175 |
| 8 | q8 | 384 MiB | 9,114 | 123-139 | 172 |
| 8 | fp16 | 1024 MiB | 5,970 | 120-134 | 153-171 |

Final choice: 8 threads, KV q8_0, 384 MiB reserve, which puts 9,114 of 10,496
experts in VRAM and yields 131/134 tok/s on prose and 176/178 on code.

Raising the resident expert count from 8,502 to 9,114 did not change speed, and
fp16 KV costs both residents and throughput, so q8 stays.

## LFM2.5-24B-A2B (new model, tested 2026-11-11)

Uncensored IQ3_M, 12.1 GB, llama.cpp Vulkan, 65,536 context.

| Metric | Value |
|---|---:|
| Decode (bench tg128) | 204.6 tok/s |
| Prefill (bench pp512) | 4,142 tok/s Vulkan, 7,502 tok/s HIP |
| 37-item set | 25/37 |
| 30-item set | 26/30 |
| Total | 51/67 |

Two runs were needed. With a generous output budget the model spends everything
thinking and returns an empty answer, which scored 28/37 but was not real. With
the reasoning budget capped at 512 tokens it answers, gains on knowledge (17/18
on cyber) and loses on calculation (6/11) and crypto (0/4), for the same total.

## TwIL-8B (tested 2026-11-11)

Q4_K_M, 5.1 GB, llama.cpp Vulkan, 32,768 context.

| Metric | Value |
|---|---:|
| Decode | 94.5 tok/s |
| 37-item set | 21/37 |
| 30-item set | 27/30 |
| Total | 48/67 |

The profile is telling: 27/30 on knowledge, the best of the small models, but
5/11 on calculation and 0/4 on crypto. It recalls facts well and does not carry a
computation through.

## Tuning that did not help

- `--prompt-batch 4096`: prefill 3,700 tok/s against 3,739 at 2,048, no gain.
- `--window 8`: 124-134 on prose and 169-173 on code, slightly below window 4.
- `--vram-reserve-mib 384` raised residents from 8,502 to 9,114 but left speed unchanged.

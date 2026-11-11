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

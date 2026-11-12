# Overall ranking

All models measured on the same card, same harness, same scoring rules. Decode
speed is measured on prose then code prompts through the serving path, not with
llama-bench, so the numbers match what you get in real use.

| # | Model | /67 | Decode | Context | Profile |
|---|---|---:|---:|---:|---|
| 1 | Swift 1.5 27B (IQ3_S) | **64** | 36 tok/s | 32K | best score, 3.5x slower |
| 2 | Gyro-S | 63 | 74 tok/s | 262K | the only one that repairs its own code (2/2) |
| 3 | Bonsai 2 27B (Q2_0) | 62 | 46 tok/s | 65K | solid ternary trade-off |
| 4 | **Cybertiel IQ3_XXS** (engine + MTP) | 61 | **128 prose / 176 code** | 262K | best quality for the speed |
| 5 | Cybertiel Q4_K_XL (engine) | 60 | 114 tok/s | 262K | previous default |
| 6 | Qwen3.5-9B (Q3_K_M) | 52 | 114 tok/s | 32K | base model, no fine-tune |
| 7 | LFM2.5-24B-A2B uncensored (IQ3_M) | 51 | **204 tok/s** | 65K | fastest, 13 points behind |
| 8 | TwIL-8B (Q4_K_M) | 48 | 95 tok/s | 32K | 27/30 on knowledge, 0/4 on crypto |
| 9 | DeepSeek-V4-Pro-9B (IQ4_XS) | 44 | 93 tok/s | 65K | below its own Qwen base |

A third Cyber-Tiel variant was tested: IQ3_S, 500 MB larger. It reaches the same
61/67 with a perfect 18/18 on the cyber and systems set, but loses a tie-break
item and decodes 2 to 4 percent slower, so IQ3_XXS stays the choice.

## Verdict

**The best model is Cybertiel in IQ3_XXS inside the PolyStrata engine.** It scores
61 of 67, one point under Swift and three under Gyro, but it decodes at 128 tok/s
on prose and 176 on code, keeps 262,144 tokens of context, and keeps 9,114 of
10,496 experts resident in VRAM. It is the configuration running in production.

Swift keeps the best raw score and is the only model with a perfect 30/30 on the
large battery, but 36 tok/s and 32,768 context make it unusable for iterating on
code or reading a repository.

Gyro is the second best choice: 63/67, 74 tok/s, 262K context, and the only model
that repairs the broken ChaCha20 when the failing assertion is handed back.

LFM2.5 illustrates the trade-off cleanly: 204 tok/s, 60 percent faster than
Cybertiel, for 10 fewer points. Worth it on simple repetitive work, not on
reasoning.

## Quality per second, for reference

Dividing the score by decode speed favours slow models and hides the context
limit, so it is only indicative:

| Model | Score/speed |
|---|---:|
| Swift 1.5 | 1.78 |
| Bonsai 27B | 1.35 |
| Gyro-S | 0.85 |
| Cybertiel IQ3_XXS | 0.48 |
| LFM2.5 | 0.25 |

A model at 36 tok/s that you abandon after one answer is worth less than one at
128 tok/s that you keep working with.

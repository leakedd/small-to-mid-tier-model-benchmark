# Model answers

Per-item results on the 30-item battery (Battery D). A check mark means the
answer was correct, a cross means it was wrong or missing.

| Item | Swift 1.5 | Gyro-S | Bonsai 27B | Cybertiel | Qwen3.5-9B | DeepSeek 9B |
|---|---|---|---|---|---|---|
| ecb | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| kerberoast | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| ntlm-relay | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ |
| cap-net-raw | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| imdsv2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| httponly | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| canary | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| aslr-bypass | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| jwt-kid | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| pinning | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| padding-oracle | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| second-order | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| false-sharing | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| fast-retransmit | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| heap-build | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| consistent-hash | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| cow | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| twopc | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| bloom | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| raid5-hole | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| numa | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| spinlock | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| pages-64g | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| tcp-segments | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| rsa-2048 | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |
| gcm-tag | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| merge-k | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| n-queens | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |
| edit-distance | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| sudoku | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |

## Wrong or missing answers

- **ecb**: Qwen3.5-9B gave no usable answer, expected B
- **ntlm-relay**: Bonsai 27B gave no usable answer, expected C; DeepSeek 9B answered A, expected C
- **rsa-2048**: Cybertiel gave no usable answer, expected A; DeepSeek 9B gave no usable answer, expected A
- **merge-k**: DeepSeek 9B failed the execution tests
- **n-queens**: Cybertiel failed the execution tests; DeepSeek 9B failed the execution tests
- **edit-distance**: DeepSeek 9B failed the execution tests
- **sudoku**: DeepSeek 9B failed the execution tests

## Notes

A empty cell means the model was not run on that item. The three format failures
(ecb, ntlm-relay for Bonsai, rsa-2048 for Cybertiel) are answers without the
required REPONSE line, not wrong reasoning: their reasoning text contained the
correct letter but the final line was missing or truncated.

Full raw results, including the 37-item battery and the repair loop, are in the
project archive.

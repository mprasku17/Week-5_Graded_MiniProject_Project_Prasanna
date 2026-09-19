# MP1 Prompt Strategy Comparison

`gpt-4o-mini` for extraction and `gpt-4o` for judging

| Strategy              |   Accuracy (mean of 3) |   Parse rate |   Judge score | Total cost ($)   |   Latency p50 (s) |
|:----------------------|-----------------------:|-------------:|--------------:|:-----------------|------------------:|
| chain_of_thought      |                    2.7 |            1 |           3.9 | $0.000383        |             1.987 |
| few_shot              |                    2.9 |            1 |           4   | $0.000424        |             1.809 |
| structured_role_based |                    2.7 |            1 |           3.9 | $0.000437        |             1.881 |
| zero_shot             |                    2.7 |            1 |           3.9 | $0.000358        |             1.923 |

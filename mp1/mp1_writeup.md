# MP1 Writeup


## 1. Which strategy won, and on what dimension? (Accuracy? Parse rate? Cost?)
`few_shot` won on deterministic accuracy with 2.900 / 3 mean field accuracy, 100% parse success, and an average judge score of 4.000 / 4 and low latency. `zero_shot` was lowest cost, while `few_shot` had the lowest latency.

## 2. What surprised you? Either a strategy worked better than expected, or worse, or a specific snippet failed in a way you didn't predict.
I thought Structured_role_based Strategy would give more Accuracy and Judge Score but it was lower than few_shot. I guess the Prompt for structured_role_based Strategy needs to be revised.

## 3. For my capstone domain, which strategy would I reach for first? Justify in 2-3 sentences.
I would reach first for the structured / role-based strategy. It makes the output contract explicit, keeps parsing simple, and is easier to review with stakeholders than an implicit prompt.

## 4. If you had another day, what would you try next? (Different model? More snippets? Different prompts?)
I would add more edge cases, compare one stronger model against `gpt-4o-mini` like 'gpt-5o', and test Tool based output separately from prompt-only structure that we have used here.
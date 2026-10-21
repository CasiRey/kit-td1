# TD 1 - models x questions (view of the comparison CSV)

OK correct, X incorrect, R rejected/invalid, - not executed

| model | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | correct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| groq:openai/gpt-oss-120b | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | 20/20 |
| groq:openai/gpt-oss-20b | OK | X | OK | OK | OK | OK | OK | OK | X | OK | X | OK | OK | OK | OK | OK | OK | OK | OK | OK | 17/20 |
| openrouter:cohere/north-mini-code:free | OK | R | OK | OK | OK | OK | OK | X | R | X | X | OK | OK | OK | X | X | X | OK | OK | OK | 12/20 |
| groq:qwen/qwen3.8-27b | OK | OK | OK | OK | OK | OK | OK | OK | X | R | OK | OK | OK | OK | X | OK | X | OK | X | OK | 15/20 |
| openrouter:dots-studio/dots-3-note-preview:free | OK | X | OK | OK | OK | OK | OK | X | OK | OK | X | OK | OK | OK | X | X | X | X | OK | OK | 13/20 |

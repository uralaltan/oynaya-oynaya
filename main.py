import json
from agent import transform_sub_outcome, EXAMPLES, TRANSFORM_REQUESTS

with open("data.json", encoding="utf-8") as fp:
    curriculum = json.load(fp)

for i, params in enumerate(EXAMPLES, 1):
    try:
        result = transform_sub_outcome(curriculum, **params)
        if result is None:
            print(f"\n[Example {i}]  →  source not found, skipped")
            continue
        print(f"\n[Example {i}]")
        print(" source:", result["source"])
        print(" target:", result["target"])
        print(" llm?  :", result["llm_used"])
    except Exception as e:
        print(f"\n[Example {i}]  →  error: {e}")

for i, params in enumerate(TRANSFORM_REQUESTS, 1):
    try:
        result = transform_sub_outcome(curriculum, **params)
        if result is None:
            print(f"\n[Example {i}]  →  source not found, skipped")
            continue
        print(f"\n[Example {i}]")
        print(" source:", result["source"])
        print(" target:", result["target"])
        print(" llm?  :", result["llm_used"])
    except Exception as e:
        print(f"\n[Example {i}]  →  error: {e}")

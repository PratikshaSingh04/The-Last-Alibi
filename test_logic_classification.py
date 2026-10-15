from ai.logic_engine import classify_contradiction

examples = [
    {"confidence": 0.95},
    {"confidence": 0.80},
    {"confidence": 0.60}
]

for example in examples:
    result = classify_contradiction(example)
    print(
        f"{result['level']} "
        f"({result['confidence']:.0%}): "
        f"{result['explanation']}"
    )

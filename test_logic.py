
import json

from ai.logic_engine import check_contradictions

with open("case_data.json", encoding="utf-8") as file:
    case_data = json.load(file)

results = check_contradictions(case_data)

print("\n=== THE LAST ALIBI ===")
print("Logical Reasoning Engine\n")

if not results:
    print("No potential contradictions detected.")

for result in results:
    print("Suspect:", result["suspect_name"])
    print("Clue:", result["clue_name"])
    print("Explanation:", result["explanation"])
    print("Confidence:", result["confidence"])
    print("-" * 50)

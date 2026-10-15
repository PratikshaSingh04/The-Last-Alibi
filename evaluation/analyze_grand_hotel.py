
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.bayesian_engine import calculate_suspect_probabilities

case_path = ROOT / "cases" / "grand_hotel.json"

with open(case_path, encoding="utf-8") as file:
    case = json.load(file)

culprit_id = "H4"
selected = []

print("GRAND HOTEL: CLUE-BY-CLUE ANALYSIS")
print("=" * 60)

# Start with no evidence.
scenarios = [("No evidence", [])]

# Add each clue in the order it appears in the case file.
for clue in case["clues"]:
    selected.append(clue["id"])
    scenarios.append(
        (f"After {clue['id']}: {clue['name']}", selected.copy())
    )

for label, clue_ids in scenarios:
    probabilities = calculate_suspect_probabilities(
        case,
        discovered_clue_ids=clue_ids,
    )

    ranking = sorted(
        probabilities.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    culprit_rank = next(
        rank
        for rank, (suspect_id, _) in enumerate(ranking, start=1)
        if suspect_id == culprit_id
    )

    print(f"\n{label}")
    print(f"Clues selected: {len(clue_ids)}")
    for suspect_id, probability in ranking:
        marker = " <-- predefined culprit" if suspect_id == culprit_id else ""
        print(f"  {suspect_id}: {probability:.2%}{marker}")

    print(f"Culprit rank: {culprit_rank}")

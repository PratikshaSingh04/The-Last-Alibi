
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
all_clue_ids = [clue["id"] for clue in case["clues"]]

full = calculate_suspect_probabilities(
    case,
    discovered_clue_ids=all_clue_ids,
)
full_ranked = sorted(
    full.items(), key=lambda item: item[1], reverse=True
)
full_rank = next(
    rank for rank, (sid, _) in enumerate(full_ranked, start=1)
    if sid == culprit_id
)

print("GRAND HOTEL: LEAVE-ONE-CLUE-OUT ANALYSIS")
print("=" * 72)
print(f"All clues: H4 probability = {full[culprit_id]:.2%}")
print(f"All clues: H4 rank = {full_rank}")
print()

for clue in case["clues"]:
    remaining = [
        clue_id for clue_id in all_clue_ids
        if clue_id != clue["id"]
    ]

    probabilities = calculate_suspect_probabilities(
        case,
        discovered_clue_ids=remaining,
    )

    ranked = sorted(
        probabilities.items(),
        key=lambda item: item[1],
        reverse=True,
    )
    rank = next(
        position
        for position, (sid, _) in enumerate(ranked, start=1)
        if sid == culprit_id
    )

    change = probabilities[culprit_id] - full[culprit_id]
    print(
        f"{clue['id']} | {clue['name']}\n"
        f"  H4 probability without clue: "
        f"{probabilities[culprit_id]:.2%}\n"
        f"  Change vs. all clues: {change:+.2%}\n"
        f"  H4 rank without clue: {rank}\n"
        f"  Top suspect without clue: {ranked[0][0]}\n"
    )

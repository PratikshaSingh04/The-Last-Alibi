
import json
import sys
from pathlib import Path
from itertools import combinations

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ai.bayesian_engine import calculate_suspect_probabilities


def main():
    with open(ROOT / "case_data.json", encoding="utf-8") as file:
        case = json.load(file)

    with open(
        ROOT / "evaluation" / "ground_truth.json",
        encoding="utf-8"
    ) as file:
        truth = json.load(file)

    culprit_id = truth["culprit_id"]
    clues = case["clues"]
    clue_ids = [clue["id"] for clue in clues]

    failures = []
    total = 0

    for size in range(len(clue_ids) + 1):
        for subset in combinations(clue_ids, size):
            total += 1

            probabilities = calculate_suspect_probabilities(
                case,
                discovered_clue_ids=set(subset)
            )

            ranking = list(probabilities.keys())
            culprit_rank = ranking.index(culprit_id) + 1

            if culprit_rank != 1:
                failures.append({
                    "clues": subset,
                    "rank": culprit_rank,
                    "probability": probabilities[culprit_id],
                    "top_suspect": ranking[0],
                    "top_probability": probabilities[ranking[0]]
                })

    print("\nTHE LAST ALIBI — FAILURE ANALYSIS")
    print("=" * 55)
    print(f"Total combinations: {total}")
    print(f"Combinations where culprit is not first: {len(failures)}")

    print("\nFirst 15 failure cases:")
    for index, failure in enumerate(failures[:15], start=1):
        clue_text = ", ".join(failure["clues"]) or "No clues"

        print(f"\n{index}. Evidence: {clue_text}")
        print(f"   Culprit rank: {failure['rank']}")
        print(f"   Culprit probability: {failure['probability']:.2%}")
        print(
            f"   Top suspect: {failure['top_suspect']} "
            f"({failure['top_probability']:.2%})"
        )

    if failures:
        print("\nFailure counts by number of clues:")
        for size in range(len(clue_ids) + 1):
            count = sum(
                len(item["clues"]) == size
                for item in failures
            )
            if count:
                print(f"{size} clues: {count} failures")

    print(
        "\nNote: these are failures against the predefined answer "
        "within one fictional case, not real-world error rates."
    )


if __name__ == "__main__":
    main()

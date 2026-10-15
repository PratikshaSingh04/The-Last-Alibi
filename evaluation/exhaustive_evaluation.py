
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
        ground_truth = json.load(file)

    culprit_id = ground_truth["culprit_id"]
    clue_ids = [clue["id"] for clue in case["clues"]]

    total = 0
    top1_correct = 0
    reciprocal_rank_sum = 0
    culprit_probability_sum = 0
    top1_by_clue_count = {}

    for size in range(len(clue_ids) + 1):
        for subset in combinations(clue_ids, size):
            probabilities = calculate_suspect_probabilities(
                case,
                discovered_clue_ids=set(subset)
            )

            ranking = list(probabilities.keys())
            rank = ranking.index(culprit_id) + 1

            total += 1
            top1_correct += rank == 1
            reciprocal_rank_sum += 1 / rank
            culprit_probability_sum += probabilities[culprit_id]

            stats = top1_by_clue_count.setdefault(
                size, {"total": 0, "correct": 0}
            )
            stats["total"] += 1
            stats["correct"] += rank == 1

    print("\nTHE LAST ALIBI — EXHAUSTIVE EVIDENCE EVALUATION")
    print("=" * 55)
    print(f"Evidence combinations evaluated: {total}")
    print(f"Predefined culprit: {culprit_id}")
    print(f"Top-1 rate: {top1_correct / total:.2%}")
    print(f"Mean reciprocal rank: {reciprocal_rank_sum / total:.4f}")
    print(
        "Mean culprit probability: "
        f"{culprit_probability_sum / total:.2%}"
    )

    print("\nResults by number of discovered clues:")
    for size, stats in sorted(top1_by_clue_count.items()):
        rate = stats["correct"] / stats["total"]
        print(
            f"{size:2} clues: {stats['correct']:4}/"
            f"{stats['total']:4} top-ranked "
            f"({rate:.2%})"
        )

    print(
        "\nInterpretation: these combinations all come from one "
        "fictional case and one manually specified likelihood model. "
        "They measure consistency over evidence subsets, not accuracy "
        "on independent mysteries."
    )


if __name__ == "__main__":
    main()

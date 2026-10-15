
import json
import math
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.bayesian_engine import calculate_suspect_probabilities


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_scenario(case_data, culprit_id, clue_ids):
    probabilities = calculate_suspect_probabilities(
        case_data,
        discovered_clue_ids=clue_ids
    )

    ranking = list(probabilities.keys())
    rank = ranking.index(culprit_id) + 1
    culprit_probability = probabilities[culprit_id]

    # Uniform baseline: every suspect receives equal probability.
    baseline_probability = 1 / len(case_data["suspects"])

    return {
        "clue_count": len(clue_ids),
        "rank": rank,
        "correct": rank == 1,
        "culprit_probability": culprit_probability,
        "bayesian_log_loss": -math.log(
            max(culprit_probability, 1e-15)
        ),
        "baseline_log_loss": -math.log(baseline_probability),
        "ranking": probabilities
    }


def main():
    case_data = load_json(PROJECT_ROOT / "case_data.json")
    ground_truth = load_json(
        PROJECT_ROOT / "evaluation" / "ground_truth.json"
    )

    culprit_id = ground_truth["culprit_id"]
    all_clues = {clue["id"] for clue in case_data["clues"]}

    scenarios = [
        ("No evidence", set()),
        ("Financial dispute", {"CL01"}),
        ("Hallway recording", {"CL02"}),
        ("Two key clues", {"CL01", "CL02"}),
        ("All evidence", all_clues)
    ]

    results = []

    print("\nTHE LAST ALIBI — SCENARIO EVALUATION")
    print("=" * 65)
    print(f"Predefined culprit: {culprit_id}")
    print("Note: scenarios share one fictional case; they are not")
    print("independent cases and do not establish general accuracy.\n")

    for name, clue_ids in scenarios:
        result = evaluate_scenario(
            case_data, culprit_id, clue_ids
        )
        results.append(result)

        predicted_id = next(iter(result["ranking"]))

        print(f"Scenario: {name}")
        print(f"Clues discovered: {result['clue_count']}")
        print(f"Top prediction: {predicted_id}")
        print(f"Culprit rank: {result['rank']}")
        print(
            f"Culprit probability: "
            f"{result['culprit_probability']:.2%}"
        )
        print(
            f"Bayesian log loss: "
            f"{result['bayesian_log_loss']:.4f}"
        )
        print(
            f"Uniform baseline log loss: "
            f"{result['baseline_log_loss']:.4f}"
        )
        print("-" * 65)

    top1_rate = sum(r["correct"] for r in results) / len(results)
    mean_log_loss = sum(
        r["bayesian_log_loss"] for r in results
    ) / len(results)

    print("\nSUMMARY")
    print(f"Scenario top-1 rate: {top1_rate:.0%}")
    print(f"Mean Bayesian log loss: {mean_log_loss:.4f}")
    print(
        "These are scenario-level results for one case, "
        "not general model accuracy."
    )


if __name__ == "__main__":
    main()


import itertools
import json
import math
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.bayesian_engine import calculate_suspect_probabilities


CASES = [
    ("Blackwood Manor", ROOT / "case_data.json",
     ROOT / "evaluation" / "ground_truth.json"),
    ("Ashford Station", ROOT / "cases" / "ashford_station.json",
     ROOT / "evaluation" / "ashford_ground_truth.json"),
    ("Observatory", ROOT / "cases" / "observatory.json",
     ROOT / "evaluation" / "observatory_ground_truth.json"),
    ("Grand Hotel", ROOT / "cases" / "grand_hotel.json",
     ROOT / "evaluation" / "grand_hotel_ground_truth.json"),
]


def load_json(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def adjust_reliability(case):
    adjusted = deepcopy(case)

    for clue in adjusted["clues"]:
        likelihoods = clue["likelihoods"]
        reliability = clue["reliability"]
        neutral = sum(likelihoods.values()) / len(likelihoods)

        clue["likelihoods"] = {
            sid: reliability * likelihood + (1 - reliability) * neutral
            for sid, likelihood in likelihoods.items()
        }

    return adjusted


def evaluate_subset(case, culprit_id, clue_ids):
    probabilities = calculate_suspect_probabilities(
        case,
        discovered_clue_ids=clue_ids,
    )
    ranked = sorted(
        probabilities.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    rank = next(
        i for i, (sid, _) in enumerate(ranked, start=1)
        if sid == culprit_id
    )
    probability = probabilities[culprit_id]

    return {
        "correct": ranked[0][0] == culprit_id,
        "reciprocal_rank": 1 / rank,
        "culprit_probability": probability,
        "log_loss": -math.log(max(probability, 1e-15)),
    }


def main():
    per_case = {}

    for label, case_path, truth_path in CASES:
        case = load_json(case_path)
        truth = load_json(truth_path)
        culprit_id = truth["culprit_id"]
        clue_ids = [clue["id"] for clue in case["clues"]]

        models = {
            "Original": case,
            "Reliability-adjusted": adjust_reliability(case),
        }
        per_case[label] = {}

        for model_name, model_case in models.items():
            rows = []

            for size in range(1, len(clue_ids) + 1):
                for subset in itertools.combinations(clue_ids, size):
                    rows.append(
                        evaluate_subset(model_case, culprit_id, list(subset))
                    )

            count = len(rows)
            per_case[label][model_name] = {
                "combinations": count,
                "top1_accuracy": sum(r["correct"] for r in rows) / count,
                "mean_reciprocal_rank": sum(
                    r["reciprocal_rank"] for r in rows
                ) / count,
                "mean_culprit_probability": sum(
                    r["culprit_probability"] for r in rows
                ) / count,
                "mean_log_loss": sum(r["log_loss"] for r in rows) / count,
            }

    print("PER-CASE RESULTS")
    print("=" * 70)

    for case_name, models in per_case.items():
        print(f"\n{case_name}")
        for model_name, metrics in models.items():
            print(
                f"  {model_name}: "
                f"accuracy={metrics['top1_accuracy']:.2%}, "
                f"MRR={metrics['mean_reciprocal_rank']:.4f}, "
                f"culprit probability="
                f"{metrics['mean_culprit_probability']:.2%}, "
                f"log loss={metrics['mean_log_loss']:.4f}, "
                f"combinations={metrics['combinations']}"
            )

    print("\nCASE-BALANCED MACRO-AVERAGE")
    print("=" * 70)

    summary = {}
    metric_names = [
        "top1_accuracy",
        "mean_reciprocal_rank",
        "mean_culprit_probability",
        "mean_log_loss",
    ]

    for model_name in ["Original", "Reliability-adjusted"]:
        summary[model_name] = {}
        for metric in metric_names:
            value = sum(
                per_case[case_name][model_name][metric]
                for case_name, _, _ in CASES
            ) / len(CASES)
            summary[model_name][metric] = value

        metrics = summary[model_name]
        print(f"\n{model_name}")
        print(f"  Top-1 accuracy: {metrics['top1_accuracy']:.2%}")
        print(f"  Mean reciprocal rank: {metrics['mean_reciprocal_rank']:.4f}")
        print(
            "  Mean culprit probability: "
            f"{metrics['mean_culprit_probability']:.2%}"
        )
        print(f"  Mean log loss: {metrics['mean_log_loss']:.4f}")

    print(f"\nUniform baseline log loss: {-math.log(0.25):.4f}")
    print(
        "\nMacro-averaging gives each of the four authored cases equal weight. "
        "Evidence subsets within a case are not independent mysteries."
    )

    output = {
        "case_count": len(CASES),
        "per_case": per_case,
        "macro_average": summary,
        "limitations": [
            "Four manually authored fictional cases.",
            "Likelihoods and reliability scores are illustrative assumptions.",
            "Evidence subsets are not independent cases.",
            "Macro-average gives each case equal weight.",
        ],
    }

    output_path = ROOT / "evaluation" / "macro_average_results.json"
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)

    print(f"\nDetailed results saved to: {output_path}")


if __name__ == "__main__":
    main()

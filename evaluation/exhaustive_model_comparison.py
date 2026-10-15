
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
    result = deepcopy(case)

    for clue in result["clues"]:
        likelihoods = clue["likelihoods"]
        reliability = clue["reliability"]
        neutral = sum(likelihoods.values()) / len(likelihoods)

        clue["likelihoods"] = {
            sid: reliability * likelihood + (1 - reliability) * neutral
            for sid, likelihood in likelihoods.items()
        }

    return result


def evaluate_subset(case, culprit_id, clue_ids):
    probabilities = calculate_suspect_probabilities(
        case, discovered_clue_ids=clue_ids
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

    culprit_probability = probabilities[culprit_id]

    return {
        "correct": ranked[0][0] == culprit_id,
        "rank": rank,
        "culprit_probability": culprit_probability,
        "log_loss": -math.log(max(culprit_probability, 1e-15)),
    }


def main():
    # Results grouped by model and number of clues.
    grouped = {
        "Original": {},
        "Reliability-adjusted": {},
    }

    for label, case_path, truth_path in CASES:
        case = load_json(case_path)
        truth = load_json(truth_path)
        culprit_id = truth["culprit_id"]

        original_clues = [clue["id"] for clue in case["clues"]]
        adjusted_case = adjust_reliability(case)

        print(f"Evaluating {label}...")

        # Evaluate every non-empty subset. Zero evidence is a tie diagnostic,
        # not a meaningful top-1 prediction.
        for size in range(1, len(original_clues) + 1):
            for subset in itertools.combinations(original_clues, size):
                clue_ids = list(subset)

                for model_name, model_case in [
                    ("Original", case),
                    ("Reliability-adjusted", adjusted_case),
                ]:
                    result = evaluate_subset(
                        model_case, culprit_id, clue_ids
                    )
                    bucket = grouped[model_name].setdefault(
                        size,
                        {
                            "count": 0,
                            "correct": 0,
                            "reciprocal_rank_sum": 0.0,
                            "culprit_probability_sum": 0.0,
                            "log_loss_sum": 0.0,
                        },
                    )

                    bucket["count"] += 1
                    bucket["correct"] += int(result["correct"])
                    bucket["reciprocal_rank_sum"] += 1 / result["rank"]
                    bucket["culprit_probability_sum"] += (
                        result["culprit_probability"]
                    )
                    bucket["log_loss_sum"] += result["log_loss"]

    summary = {}

    for model_name, buckets in grouped.items():
        total_count = sum(bucket["count"] for bucket in buckets.values())
        total_correct = sum(bucket["correct"] for bucket in buckets.values())
        reciprocal_sum = sum(
            bucket["reciprocal_rank_sum"] for bucket in buckets.values()
        )
        probability_sum = sum(
            bucket["culprit_probability_sum"] for bucket in buckets.values()
        )
        loss_sum = sum(
            bucket["log_loss_sum"] for bucket in buckets.values()
        )

        summary[model_name] = {
            "evidence_combinations": total_count,
            "top1_accuracy": total_correct / total_count,
            "mean_reciprocal_rank": reciprocal_sum / total_count,
            "mean_culprit_probability": probability_sum / total_count,
            "mean_log_loss": loss_sum / total_count,
            "by_clue_count": {},
        }

        for size, bucket in sorted(buckets.items()):
            count = bucket["count"]
            summary[model_name]["by_clue_count"][str(size)] = {
                "count": count,
                "top1_accuracy": bucket["correct"] / count,
                "mean_reciprocal_rank": (
                    bucket["reciprocal_rank_sum"] / count
                ),
                "mean_culprit_probability": (
                    bucket["culprit_probability_sum"] / count
                ),
                "mean_log_loss": bucket["log_loss_sum"] / count,
            }

    print("\nEXHAUSTIVE EVIDENCE-SPACE COMPARISON")
    print("=" * 60)

    for model_name, metrics in summary.items():
        print(f"\n{model_name}")
        print(f"  Combinations: {metrics['evidence_combinations']}")
        print(f"  Top-1 accuracy: {metrics['top1_accuracy']:.2%}")
        print(f"  Mean reciprocal rank: {metrics['mean_reciprocal_rank']:.4f}")
        print(
            "  Mean culprit probability: "
            f"{metrics['mean_culprit_probability']:.2%}"
        )
        print(f"  Mean log loss: {metrics['mean_log_loss']:.4f}")

    print(f"\nUniform baseline log loss: {-math.log(0.25):.4f}")
    print(
        "\nThese are evidence subsets from four authored cases, "
        "not independent mystery cases. Likelihoods and reliability "
        "scores are manually specified assumptions."
    )

    output_path = ROOT / "evaluation" / "exhaustive_model_comparison.json"
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    print(f"\nDetailed results saved to: {output_path}")


if __name__ == "__main__":
    main()

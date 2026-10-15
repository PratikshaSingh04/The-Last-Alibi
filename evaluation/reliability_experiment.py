
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
    (
        "Blackwood Manor",
        ROOT / "case_data.json",
        ROOT / "evaluation" / "ground_truth.json",
    ),
    (
        "Ashford Station",
        ROOT / "cases" / "ashford_station.json",
        ROOT / "evaluation" / "ashford_ground_truth.json",
    ),
    (
        "Observatory",
        ROOT / "cases" / "observatory.json",
        ROOT / "evaluation" / "observatory_ground_truth.json",
    ),
    (
        "Grand Hotel",
        ROOT / "cases" / "grand_hotel.json",
        ROOT / "evaluation" / "grand_hotel_ground_truth.json",
    ),
]


def load_json(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def reliability_adjusted_case(case):
    adjusted = deepcopy(case)

    for clue in adjusted["clues"]:
        reliability = clue["reliability"]
        likelihoods = clue["likelihoods"]
        neutral = sum(likelihoods.values()) / len(likelihoods)

        clue["likelihoods"] = {
            suspect_id: (
                reliability * likelihood
                + (1 - reliability) * neutral
            )
            for suspect_id, likelihood in likelihoods.items()
        }

    return adjusted


def evaluate_model(case, culprit_id, clue_ids, adjusted):
    model_case = reliability_adjusted_case(case) if adjusted else case

    probabilities = calculate_suspect_probabilities(
        model_case,
        discovered_clue_ids=clue_ids,
    )

    ranking = sorted(
        probabilities.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    rank = next(
        i for i, (suspect_id, _) in enumerate(ranking, start=1)
        if suspect_id == culprit_id
    )

    culprit_probability = probabilities[culprit_id]

    return {
        "correct": ranking[0][0] == culprit_id,
        "rank": rank,
        "culprit_probability": culprit_probability,
        "log_loss": -math.log(max(culprit_probability, 1e-15)),
        "top_suspect": ranking[0][0],
    }


def main():
    results = {"Original": [], "Reliability-adjusted": []}

    for label, case_path, truth_path in CASES:
        case = load_json(case_path)
        truth = load_json(truth_path)
        culprit_id = truth["culprit_id"]
        clues = case["clues"]

        scenarios = [
            ("Partial evidence", [c["id"] for c in clues[:2]]),
            ("All evidence", [c["id"] for c in clues]),
        ]

        print(f"\n{'=' * 60}\n{label} — culprit: {truth['culprit_name']}")
        for scenario_name, clue_ids in scenarios:
            print(f"\n{scenario_name} ({len(clue_ids)} clues)")

            for model_name, adjusted in [
                ("Original", False),
                ("Reliability-adjusted", True),
            ]:
                result = evaluate_model(
                    case, culprit_id, clue_ids, adjusted
                )
                results[model_name].append({
                    "case": label,
                    "scenario": scenario_name,
                    **result,
                })

                print(
                    f"  {model_name}: "
                    f"top={result['top_suspect']}, "
                    f"rank={result['rank']}, "
                    f"culprit probability="
                    f"{result['culprit_probability']:.2%}, "
                    f"log loss={result['log_loss']:.4f}"
                )

    print(f"\n{'=' * 60}\nOVERALL COMPARISON")
    print("=" * 60)

    summary = {}
    for model_name, entries in results.items():
        count = len(entries)
        accuracy = sum(r["correct"] for r in entries) / count
        mean_probability = sum(
            r["culprit_probability"] for r in entries
        ) / count
        mean_log_loss = sum(r["log_loss"] for r in entries) / count
        mrr = sum(1 / r["rank"] for r in entries) / count

        summary[model_name] = {
            "prediction_count": count,
            "top1_accuracy": accuracy,
            "mean_reciprocal_rank": mrr,
            "mean_culprit_probability": mean_probability,
            "mean_log_loss": mean_log_loss,
        }

        print(f"\n{model_name}")
        print(f"  Predictions: {count}")
        print(f"  Top-1 accuracy: {accuracy:.2%}")
        print(f"  Mean reciprocal rank: {mrr:.4f}")
        print(f"  Mean culprit probability: {mean_probability:.2%}")
        print(f"  Mean log loss: {mean_log_loss:.4f}")

    print(f"\nUniform baseline log loss: {-math.log(0.25):.4f}")
    print(
        "\nThese results cover four manually authored cases. "
        "The scenarios are not independent cases, and the "
        "reliability adjustment is an experimental assumption."
    )

    output_path = ROOT / "evaluation" / "reliability_comparison.json"
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            {"summary": summary, "results": results},
            file,
            indent=2,
        )

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()

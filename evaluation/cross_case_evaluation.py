

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.bayesian_engine import calculate_suspect_probabilities


ROOT = Path(__file__).resolve().parents[1]

CASES = [
    
    {
        "case_file": ROOT / "cases" / "grand_hotel.json",
        "truth_file": ROOT / "evaluation" / "grand_hotel_ground_truth.json",
        "label": "Grand Hotel",
    },
    {
        "case_file": ROOT / "cases" / "observatory.json",
        "truth_file": ROOT / "evaluation" / "observatory_ground_truth.json",
        "label": "Observatory",
    },
    {
        "case_file": ROOT / "case_data.json",
        "truth_file": ROOT / "evaluation" / "ground_truth.json",
        "label": "Blackwood Manor",
    },
    {
        "case_file": ROOT / "cases" / "ashford_station.json",
        "truth_file": ROOT / "evaluation" / "ashford_ground_truth.json",
        "label": "Ashford Station",
    },
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_case(case_info):
    case = load_json(case_info["case_file"])
    truth = load_json(case_info["truth_file"])
    culprit_id = truth["culprit_id"]

    suspect_ids = {suspect["id"] for suspect in case["suspects"]}
    if culprit_id not in suspect_ids:
        raise ValueError(
            f"Ground-truth culprit {culprit_id} is not in "
            f"{case_info['label']}."
        )

    scenarios = [
        ("No evidence", []),
        ("Partial evidence", [clue["id"] for clue in case["clues"][:2]]),
        ("All evidence", [clue["id"] for clue in case["clues"]]),
    ]

    results = []

    print(f"\n{'=' * 60}")
    print(f"CASE: {case_info['label']}")
    print(f"Predefined culprit: {truth['culprit_name']}")
    print("=" * 60)

    for scenario_name, clue_ids in scenarios:
        probabilities = calculate_suspect_probabilities(
            case,
            discovered_clue_ids=clue_ids,
        )

        ranking = sorted(
            probabilities.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        culprit_probability = probabilities[culprit_id]
        culprit_rank = next(
            index
            for index, (suspect_id, _) in enumerate(ranking, start=1)
            if suspect_id == culprit_id
        )

        print(f"\nScenario: {scenario_name}")
        print(f"Clues used: {len(clue_ids)}")
        print(f"Top-ranked suspect: {ranking[0][0]}")
        print(f"Culprit rank: {culprit_rank}")
        print(f"Culprit probability: {culprit_probability:.2%}")

        if not clue_ids:
            print("Diagnostic only: no-evidence rankings are tied.")
            if not all(
                abs(value - 0.25) < 1e-9
                for value in probabilities.values()
            ):
                raise AssertionError(
                    "Expected four equal probabilities without evidence."
                )
            continue

        results.append(
            {
                "case": case_info["label"],
                "scenario": scenario_name,
                "correct": ranking[0][0] == culprit_id,
                "rank": culprit_rank,
                "culprit_probability": culprit_probability,
                "log_loss": -math.log(
                    max(culprit_probability, 1e-15)
                ),
            }
        )

    return results


def main():
    all_results = []

    for case_info in CASES:
        all_results.extend(evaluate_case(case_info))

    if not all_results:
        raise RuntimeError("No evaluation scenarios were completed.")

    count = len(all_results)
    top1_accuracy = sum(
        result["correct"] for result in all_results
    ) / count
    mean_reciprocal_rank = sum(
        1 / result["rank"] for result in all_results
    ) / count
    mean_culprit_probability = sum(
        result["culprit_probability"] for result in all_results
    ) / count
    mean_log_loss = sum(
        result["log_loss"] for result in all_results
    ) / count

    # Uniform baseline: each of the four suspects receives probability 0.25.
    baseline_log_loss = -math.log(0.25)

    print(f"\n{'=' * 60}")
    print("CROSS-CASE SUMMARY")
    print("=" * 60)
    print(f"Cases: {len(CASES)}")
    print(f"Evidence-based predictions: {count}")
    print(f"Top-1 accuracy: {top1_accuracy:.2%}")
    print(f"Mean reciprocal rank: {mean_reciprocal_rank:.4f}")
    print(
        "Mean probability assigned to culprit: "
        f"{mean_culprit_probability:.2%}"
    )
    print(f"Mean Bayesian log loss: {mean_log_loss:.4f}")
    print(f"Uniform baseline log loss: {baseline_log_loss:.4f}")
    
    print(
    "Lower log loss is better. Results are descriptive, "
    f"based on {len(CASES)} manually authored cases."
    )

    output_path = ROOT / "evaluation" / "cross_case_results.json"
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            {
                "case_count": len(CASES),
                "prediction_count": count,
                "metrics": {
                    "top1_accuracy": top1_accuracy,
                    "mean_reciprocal_rank": mean_reciprocal_rank,
                    "mean_culprit_probability": mean_culprit_probability,
                    "mean_log_loss": mean_log_loss,
                    "uniform_baseline_log_loss": baseline_log_loss,
                },
                "results": all_results,
                "limitations": [
                    "Only two manually authored fictional cases were evaluated.",
                    "Likelihoods are illustrative assumptions, not learned estimates.",
                    "Evidence scenarios from the same case are not independent cases.",
                    "The uniform baseline is a probability baseline, not a trained competitor.",
                ],
            },
            file,
            indent=2,
        )

    print(f"\nDetailed results saved to: {output_path}")


if __name__ == "__main__":
    main()

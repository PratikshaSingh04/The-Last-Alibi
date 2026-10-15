
import math

import json

from ai.bayesian_engine import explain_probability_changes

with open("case_data.json", "r", encoding="utf-8") as file:
    case = json.load(file)

discovered = {"CL01", "CL02"}

results = explain_probability_changes(case, discovered)

print("EXPLAINABLE AI TEST")
print("=" * 40)

for result in results:
    print(f"\nClue: {result['clue_name']}")

    for change in result["changes"]:
        print(" -", change["explanation"])

print("\nTest completed!")

def calculate_suspect_probabilities(
    case_data,
    discovered_clue_ids=None,
    priors=None
):
    """Calculate normalized suspect probabilities using clue likelihoods."""

    suspects = case_data["suspects"]
    clues = case_data["clues"]
    suspect_ids = [suspect["id"] for suspect in suspects]

    if not suspect_ids:
        raise ValueError("At least one suspect is required.")

    if priors is None:
        priors = {sid: 1 / len(suspect_ids) for sid in suspect_ids}

    if set(priors) != set(suspect_ids):
        raise ValueError("Priors must contain every suspect ID.")

    if any(
        not math.isfinite(value) or value <= 0
        for value in priors.values()
    ):
        raise ValueError("Priors must be finite and positive.")

    prior_total = sum(priors.values())
    normalized_priors = {
        sid: priors[sid] / prior_total for sid in suspect_ids
    }

    if discovered_clue_ids is None:
        discovered_clue_ids = {clue["id"] for clue in clues}
    else:
        discovered_clue_ids = set(discovered_clue_ids)

    known_clue_ids = {clue["id"] for clue in clues}

    if not discovered_clue_ids.issubset(known_clue_ids):
        raise ValueError("Unknown clue ID provided.")

    log_scores = {}

    for sid in suspect_ids:
        score = math.log(normalized_priors[sid])

        for clue in clues:
            if clue["id"] not in discovered_clue_ids:
                continue

            likelihood = clue["likelihoods"][sid]

            if not math.isfinite(likelihood) or not 0 < likelihood <= 1:
                raise ValueError(
                    f"Invalid likelihood for {clue['id']} and {sid}."
                )

            score += math.log(likelihood)

        log_scores[sid] = score

    max_score = max(log_scores.values())
    weights = {
        sid: math.exp(score - max_score)
        for sid, score in log_scores.items()
    }

    total_weight = sum(weights.values())

    probabilities = {
        sid: weight / total_weight
        for sid, weight in weights.items()
    }

    return dict(
        sorted(
            probabilities.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )


def explain_probability_changes(case_data, discovered_clue_ids=None):
    """Explain how each discovered clue changes suspect probabilities."""

    clues = case_data["clues"]
    suspects = case_data["suspects"]

    if discovered_clue_ids is None:
        discovered_clue_ids = {clue["id"] for clue in clues}
    else:
        discovered_clue_ids = set(discovered_clue_ids)

    known_ids = {clue["id"] for clue in clues}

    if not discovered_clue_ids.issubset(known_ids):
        raise ValueError("Unknown clue ID provided.")

    cumulative_clues = []
    explanations = []

    previous = calculate_suspect_probabilities(
        case_data, discovered_clue_ids=[]
    )

    for clue in clues:
        if clue["id"] not in discovered_clue_ids:
            continue

        cumulative_clues.append(clue["id"])

        current = calculate_suspect_probabilities(
            case_data,
            discovered_clue_ids=cumulative_clues
        )

        changes = []

        for suspect in suspects:
            sid = suspect["id"]
            before = previous[sid]
            after = current[sid]
            difference = after - before

            if difference > 0.0001:
                direction = "increased"
            elif difference < -0.0001:
                direction = "decreased"
            else:
                direction = "barely changed"

            changes.append({
                "suspect_id": sid,
                "suspect_name": suspect["name"],
                "before": before,
                "after": after,
                "change": difference,
                "direction": direction,
                "explanation": (
                    f"{suspect['name']}'s probability {direction} "
                    f"from {before:.1%} to {after:.1%} after "
                    f"discovering {clue['name']}."
                )
            })

        changes.sort(
            key=lambda item: abs(item["change"]),
            reverse=True
        )

        explanations.append({
            "clue_id": clue["id"],
            "clue_name": clue["name"],
            "changes": changes
        })

        previous = current

    return explanations


import math


def calculate_suspect_probabilities(
    case_data,
    discovered_clue_ids=None,
    priors=None
):
    """
    Calculate posterior probabilities for each suspect.

    Assumption:
    Discovered clues are conditionally independent given
    each suspect hypothesis.
    """

    suspects = case_data["suspects"]
    clues = case_data["clues"]

    suspect_ids = [suspect["id"] for suspect in suspects]

    # If no prior probabilities are provided, use equal priors.
    if priors is None:
        priors = {
            suspect_id: 1 / len(suspect_ids)
            for suspect_id in suspect_ids
        }

    # Validate prior probabilities.
    if set(priors) != set(suspect_ids):
        raise ValueError("Priors must contain every suspect ID.")

    if any(
        not math.isfinite(value) or value <= 0
        for value in priors.values()
    ):
        raise ValueError("Priors must be finite and positive.")

    prior_total = sum(priors.values())

    normalized_priors = {
        suspect_id: priors[suspect_id] / prior_total
        for suspect_id in suspect_ids
    }

    # If no clue IDs are supplied, use all clues.
    if discovered_clue_ids is None:
        discovered_clue_ids = {
            clue["id"] for clue in clues
        }
    else:
        discovered_clue_ids = set(discovered_clue_ids)

    known_clue_ids = {clue["id"] for clue in clues}

    if not discovered_clue_ids.issubset(known_clue_ids):
        raise ValueError("Unknown clue ID provided.")

    # Use log probabilities to avoid numerical underflow.
    log_scores = {}

    for suspect_id in suspect_ids:
        prior = normalized_priors[suspect_id]
        log_score = math.log(prior)

        for clue in clues:
            if clue["id"] not in discovered_clue_ids:
                continue

            likelihood = clue["likelihoods"][suspect_id]

            if not math.isfinite(likelihood) or not 0 < likelihood <= 1:
                raise ValueError(
                    f"Invalid likelihood for {clue['id']} "
                    f"and suspect {suspect_id}."
                )

            log_score += math.log(likelihood)

        log_scores[suspect_id] = log_score

    # Normalize using log-sum-exp for numerical stability.
    max_log_score = max(log_scores.values())

    weights = {
        suspect_id: math.exp(score - max_log_score)
        for suspect_id, score in log_scores.items()
    }

    total_weight = sum(weights.values())

    probabilities = {
        suspect_id: weight / total_weight
        for suspect_id, weight in weights.items()
    }

    return dict(
        sorted(
            probabilities.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )


def explain_probability_changes(case_data, discovered_clue_ids=None):
    """Explain how discovered clues change suspect probabilities."""

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

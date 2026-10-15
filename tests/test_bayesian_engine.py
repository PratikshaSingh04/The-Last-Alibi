
import json
import pytest
from pathlib import Path

from ai.bayesian_engine import calculate_suspect_probabilities


CASE_PATH = Path(__file__).resolve().parents[1] / "case_data.json"


def load_case():
    with CASE_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def test_probabilities_sum_to_one():
    case = load_case()

    results = calculate_suspect_probabilities(
        case,
        discovered_clue_ids={"CL01", "CL02"}
    )

    assert sum(results.values()) == pytest.approx(1.0)


def test_no_clues_gives_equal_priors():
    case = load_case()

    results = calculate_suspect_probabilities(
        case,
        discovered_clue_ids=set()
    )

    for probability in results.values():
        assert probability == pytest.approx(0.25)


def test_hallway_recording_changes_rankings():
    case = load_case()

    results = calculate_suspect_probabilities(
        case,
        discovered_clue_ids={"CL02"}
    )

    assert results["M1"] == max(results.values())
    assert results["M1"] > 0.25


def test_unknown_clue_is_rejected():
    case = load_case()

    with pytest.raises(ValueError):
        calculate_suspect_probabilities(
            case,
            discovered_clue_ids={"UNKNOWN"}
        )


def test_custom_priors_are_normalized():
    case = load_case()

    results = calculate_suspect_probabilities(
        case,
        discovered_clue_ids=set(),
        priors={
            "E1": 2,
            "M1": 2,
            "C1": 2,
            "D1": 2
        }
    )

    assert sum(results.values()) == pytest.approx(1.0)


def explain_probability_changes(case_data, discovered_clue_ids=None):
    """
    Explain how each discovered clue changes the probability of each suspect.

    Clues are processed in the order they appear in case_data.json.
    """
    suspects = case_data["suspects"]
    clues = case_data["clues"]

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
                    f"{suspect['name']}'s probability "
                    f"{direction} from {before:.1%} "
                    f"to {after:.1%} after discovering "
                    f"{clue['name']}."
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

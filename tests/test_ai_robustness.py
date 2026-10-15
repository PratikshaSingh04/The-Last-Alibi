
import json
from pathlib import Path

from ai.bayesian_engine import calculate_suspect_probabilities


ROOT = Path(__file__).resolve().parents[1]

with open(ROOT / "case_data.json", encoding="utf-8") as file:
    CASE = json.load(file)


def test_no_evidence_gives_equal_probabilities():
    result = calculate_suspect_probabilities(
        CASE,
        discovered_clue_ids=set()
    )

    values = list(result.values())

    assert len(values) == 4
    assert all(abs(value - 0.25) < 1e-9 for value in values)


def test_more_relevant_evidence_increases_marcus_probability():
    one_clue = calculate_suspect_probabilities(
        CASE,
        discovered_clue_ids={"CL01"}
    )

    two_clues = calculate_suspect_probabilities(
        CASE,
        discovered_clue_ids={"CL01", "CL02"}
    )

    assert two_clues["M1"] > one_clue["M1"]


def test_clue_order_does_not_change_probabilities():
    first = calculate_suspect_probabilities(
        CASE,
        discovered_clue_ids=["CL01", "CL02"]
    )

    second = calculate_suspect_probabilities(
        CASE,
        discovered_clue_ids=["CL02", "CL01"]
    )

    for suspect_id in first:
        assert abs(first[suspect_id] - second[suspect_id]) < 1e-9


def test_unknown_clues_are_rejected():
    try:
        calculate_suspect_probabilities(
            CASE,
            discovered_clue_ids={"UNKNOWN"}
        )
    except ValueError:
        return

    raise AssertionError("Unknown clue ID should raise ValueError.")

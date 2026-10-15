
import json
from pathlib import Path

from ai.logic_engine import check_contradictions


CASE_PATH = Path(__file__).resolve().parents[1] / "case_data.json"


def load_case():
    with CASE_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def test_marcus_has_a_potential_contradiction():
    case = load_case()

    results = check_contradictions(case)

    marcus_conflicts = [
        result for result in results
        if result["suspect_id"] == "M1"
    ]

    assert len(marcus_conflicts) == 1
    assert marcus_conflicts[0]["clue_id"] == "CL02"


def test_undiscovered_clues_are_ignored():
    case = load_case()

    results = check_contradictions(
        case,
        discovered_clue_ids={"CL01"}
    )

    assert results == []


def test_low_confidence_observation_is_ignored():
    case = load_case()

    results = check_contradictions(
        case,
        confidence_threshold=0.95
    )

    assert all(
        result["confidence"] >= 0.95
        for result in results
    )


def test_explanation_is_generated():
    case = load_case()

    results = check_contradictions(case)

    assert results
    assert "Marcus" in results[0]["explanation"]
    assert "21:18" in results[0]["explanation"]

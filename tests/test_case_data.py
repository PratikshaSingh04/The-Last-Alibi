
import json
from pathlib import Path

CASE_PATH = Path(__file__).resolve().parents[1] / "case_data.json"


def load_case():
    with CASE_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def test_case_has_four_suspects():
    case = load_case()
    assert len(case["suspects"]) == 4


def test_case_has_twelve_clues():
    case = load_case()
    assert len(case["clues"]) == 12


def test_suspect_ids_are_unique():
    case = load_case()
    ids = [suspect["id"] for suspect in case["suspects"]]
    assert len(ids) == len(set(ids))


def test_clue_ids_are_unique():
    case = load_case()
    ids = [clue["id"] for clue in case["clues"]]
    assert len(ids) == len(set(ids))


def test_likelihoods_are_valid():
    case = load_case()
    suspect_ids = {s["id"] for s in case["suspects"]}

    for clue in case["clues"]:
        assert set(clue["likelihoods"]) == suspect_ids

        for value in clue["likelihoods"].values():
            assert 0 < value < 1


def test_observations_reference_known_suspects():
    case = load_case()
    suspect_ids = {s["id"] for s in case["suspects"]}

    for clue in case["clues"]:
        for observation in clue["observations"]:
            assert observation["suspect_id"] in suspect_ids

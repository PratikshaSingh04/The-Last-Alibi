
import json

from ai.bayesian_engine import calculate_suspect_probabilities


with open("case_data.json", encoding="utf-8") as file:
    case_data = json.load(file)

experiments = [
    ("No clues", set()),
    ("Financial dispute", {"CL01"}),
    ("Hallway recording", {"CL02"}),
    ("Both clues", {"CL01", "CL02"})
]

suspect_names = {
    suspect["id"]: suspect["name"]
    for suspect in case_data["suspects"]
}

for experiment_name, clue_ids in experiments:
    probabilities = calculate_suspect_probabilities(
        case_data,
        discovered_clue_ids=clue_ids
    )

    print(f"\n=== {experiment_name} ===")

    for suspect_id, probability in probabilities.items():
        print(
            f"{suspect_names[suspect_id]}: "
            f"{probability:.2%}"
        )


from datetime import datetime


def time_to_minutes(time_string):
    """Convert HH:MM into minutes after midnight."""
    parsed = datetime.strptime(time_string, "%H:%M")
    return parsed.hour * 60 + parsed.minute


def check_contradictions(case_data, discovered_clue_ids=None,
                         confidence_threshold=0.75):
    """
    Compare suspect alibis with discovered location observations.

    Returns:
        A list of potential alibi contradictions.
    """
    if discovered_clue_ids is None:
        discovered_clue_ids = {
            clue["id"] for clue in case_data["clues"]
        }

    suspects = {
        suspect["id"]: suspect
        for suspect in case_data["suspects"]
    }

    contradictions = []

    for clue in case_data["clues"]:
        # Only analyze clues the player has discovered.
        if clue["id"] not in discovered_clue_ids:
            continue

        for observation in clue.get("observations", []):
            suspect_id = observation["suspect_id"]

            if suspect_id not in suspects:
                continue

            confidence = observation.get("confidence", 0)

            # Uncertain observations are not treated as contradictions.
            if confidence < confidence_threshold:
                continue

            suspect = suspects[suspect_id]
            alibi = suspect["alibi"]

            observed_time = time_to_minutes(observation["time"])
            alibi_start = time_to_minutes(alibi["start"])
            alibi_end = time_to_minutes(alibi["end"])

            # Check whether the observation falls within the alibi.
            within_alibi = (
                alibi_start <= observed_time <= alibi_end
            )

            if not within_alibi:
                continue

            claimed_location = alibi["location"]
            observed_location = observation["location"]

            # Different locations at the same time create a conflict.
            if claimed_location.lower() != observed_location.lower():
                contradictions.append({
                    "suspect_id": suspect_id,
                    "suspect_name": suspect["name"],
                    "clue_id": clue["id"],
                    "clue_name": clue["name"],
                    "claimed_location": claimed_location,
                    "observed_location": observed_location,
                    "time": observation["time"],
                    "confidence": confidence,
                    "explanation": (
                        f"{suspect['name']} claimed to be in the "
                        f"{claimed_location} from {alibi['start']} "
                        f"to {alibi['end']}, but {clue['name']} "
                        f"places them in the {observed_location} "
                        f"at {observation['time']}."
                    )
                })

    return contradictions


def classify_contradiction(contradiction):
    """
    Classify a detected contradiction by observation confidence.

    This describes evidence strength, not whether the suspect is guilty.
    """
    confidence = contradiction.get("confidence", 0)

    if confidence >= 0.90:
        level = "High confidence"
        explanation = (
            "The observation strongly conflicts with the claimed "
            "location, but should still be corroborated."
        )
    elif confidence >= 0.75:
        level = "Moderate confidence"
        explanation = (
            "The observation conflicts with the claimed location. "
            "Seek additional corroborating evidence."
        )
    else:
        level = "Low confidence"
        explanation = (
            "The observation is uncertain and should not be treated "
            "as a reliable contradiction on its own."
        )

    return {
        "level": level,
        "confidence": confidence,
        "explanation": explanation
    }


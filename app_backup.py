
import json
from pathlib import Path

import streamlit as st

from ai.logic_engine import (
    check_contradictions,
    classify_contradiction,
)
from ai.bayesian_engine import (
    calculate_suspect_probabilities,
    explain_probability_changes,
)


# --------------------------------------------------
# 1. PAGE CONFIGURATION AND CASE DATA
# --------------------------------------------------

st.set_page_config(
    page_title="The Last Alibi",
    page_icon="🕵️",
    layout="wide",
)

CASE_PATH = Path(__file__).parent / "case_data.json"

with CASE_PATH.open(encoding="utf-8") as file:
    case_data = json.load(file)

suspects = case_data["suspects"]
clues = case_data["clues"]

suspect_names = {
    suspect["id"]: suspect["name"]
    for suspect in suspects
}


# --------------------------------------------------
# 2. SESSION STATE
# --------------------------------------------------

if "discovered_clues" not in st.session_state:
    st.session_state.discovered_clues = set()

if "final_accusation" not in st.session_state:
    st.session_state.final_accusation = None


# --------------------------------------------------
# 3. HEADER
# --------------------------------------------------

st.title("🕵️ The Last Alibi")
st.subheader("An AI-Powered Mystery Detective Game")

st.markdown("### Case File: The Midnight at Blackwood Manor")

st.write(
    "Richard Blackwood has been found dead in his study. "
    "Four suspects have been questioned, each with a possible "
    "motive and an alibi. Investigate the evidence and use "
    "the AI reasoning system to determine which explanation "
    "is best supported."
)

st.divider()

col1, col2, col3 = st.columns(3)

col1.metric("Suspects", len(suspects))
col2.metric(
    "Clues Discovered",
    len(st.session_state.discovered_clues),
)
col3.metric("Total Clues", len(clues))


# --------------------------------------------------
# 4. SUSPECT PROFILES
# --------------------------------------------------

st.header("🔎 Suspects")

suspect_columns = st.columns(4)

for column, suspect in zip(suspect_columns, suspects):
    with column:
        with st.container(border=True):
            st.subheader(suspect["name"])
            st.caption(suspect["role"])

            st.write("**Possible motive**")
            st.write(suspect["motive"])

            st.write("**Claimed location**")
            st.write(suspect["alibi"]["location"])

            st.write(
                f'{suspect["alibi"]["start"]}–'
                f'{suspect["alibi"]["end"]}'
            )


# --------------------------------------------------
# 5. INVESTIGATION ROOM
# --------------------------------------------------

st.divider()
st.header("🗂️ Investigation Room")

st.write(
    "Select the evidence you have discovered. "
    "The AI will update its analysis using only the selected clues."
)

selected_clue_ids = set()

for clue in clues:
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])

        with col1:
            st.subheader(clue["name"])
            st.write(clue["description"])

            st.caption(
                f'Type: {clue["type"].replace("_", " ").title()}'
            )

        with col2:
            is_discovered = st.checkbox(
                "Discover clue",
                value=clue["id"] in st.session_state.discovered_clues,
                key=f'clue_{clue["id"]}',
            )

            if is_discovered:
                selected_clue_ids.add(clue["id"])

# Synchronize selected clues with session state.
st.session_state.discovered_clues = selected_clue_ids


# --------------------------------------------------
# 6. AI INVESTIGATION RESULTS
# --------------------------------------------------

st.divider()
st.header("🧠 AI Investigation Results")

# Calculate probabilities only when evidence is selected.
probabilities = {}

if selected_clue_ids:
    probabilities = calculate_suspect_probabilities(
        case_data,
        discovered_clue_ids=selected_clue_ids,
    )


# Evidence sufficiency indicator
if len(selected_clue_ids) == 0:
    st.warning(
        "Insufficient evidence: no clues have been discovered. "
        "All suspects begin with equal prior probability. "
        "The first displayed suspect is only a tie-break."
    )
elif len(selected_clue_ids) < 3:
    st.info(
        f"Limited evidence: only {len(selected_clue_ids)} "
        "clue(s) are available. Treat this ranking as provisional "
        "and investigate further."
    )
else:
    st.success(
        f"{len(selected_clue_ids)} clues are available. "
        "Review the evidence and contradictions before accusing "
        "any suspect."
    )

# --------------------------------------------------
# 6A. BAYESIAN SUSPECT RANKING
# --------------------------------------------------

st.subheader("1. Suspect Probability Ranking")

st.caption(
    "These are model-based posterior probabilities based on "
    "configured priors and clue likelihoods. They are not "
    "verified probabilities of real-world guilt."
)

if probabilities:
    for rank, (suspect_id, probability) in enumerate(
        probabilities.items(),
        start=1,
    ):
        name = suspect_names[suspect_id]

        st.write(f"**{rank}. {name} — {probability:.1%}**")
        st.progress(probability)
else:
    st.info(
        "No evidence has been selected yet. "
        "Discover a clue above to begin the AI investigation."
    )


# Evidence sufficiency indicator.
if len(selected_clue_ids) == 0:
    st.warning(
        "Insufficient evidence: no clues have been discovered. "
        "All suspects begin with equal prior probability. "
        "The first displayed suspect is only a tie-break."
    )
elif len(selected_clue_ids) < 3:
    st.info(
        f"Limited evidence: only {len(selected_clue_ids)} clue(s) "
        "are available. Treat this ranking as provisional and "
        "investigate further."
    )
else:
    st.success(
        f"{len(selected_clue_ids)} clues are available. "
        "Review the evidence and contradictions before accusing "
        "any suspect."
    )

# --------------------------------------------------
# 6B. EXPLAINABLE AI
# --------------------------------------------------

st.subheader("2. Why Does the AI Suspect Them?")

if selected_clue_ids:
    explanations = explain_probability_changes(
        case_data,
        selected_clue_ids,
    )

    st.caption(
        "These explanations show how each discovered clue changes "
        "the model's estimates. They do not prove guilt."
    )

    if explanations:
        for result in explanations:
            with st.expander(f'🔎 {result["clue_name"]}'):
                for change in result["changes"]:
                    st.write(f'**{change["suspect_name"]}**')
                    st.write(change["explanation"])

                    st.progress(
                        min(1.0, max(0.0, change["after"]))
                    )
    else:
        st.info("No explanation is available yet.")
else:
    st.info(
        "Discover a clue to see how it changes the AI's "
        "suspect probabilities."
    )


# --------------------------------------------------
# 6C. LOGICAL REASONING
# --------------------------------------------------

st.subheader("3. Logical Reasoning")

contradictions = check_contradictions(
    case_data,
    discovered_clue_ids=selected_clue_ids,
)

if contradictions:
    st.warning(
        f"{len(contradictions)} potential alibi "
        "contradiction(s) detected."
    )

    for contradiction in contradictions:
        classification = classify_contradiction(contradiction)

        with st.expander(
            f'{classification["level"]} — '
            f'{contradiction["suspect_name"]}: '
            f'{contradiction["clue_name"]}'
        ):
            st.write(contradiction["explanation"])

            st.write(
                f'**Observation confidence:** '
                f'{classification["confidence"]:.0%}'
            )

            st.write(
                f'**Assessment:** {classification["explanation"]}'
            )

            st.caption(
                "A contradiction is a reason to investigate further, "
                "not proof of guilt."
            )
else:
    st.info(
        "No potential contradictions were detected "
        "among the selected clues."
    )


# --------------------------------------------------
# 6D. EVIDENCE REVIEW
# --------------------------------------------------

st.subheader("4. Evidence Review")

selected_clues = [
    clue for clue in clues
    if clue["id"] in selected_clue_ids
]

if selected_clues:
    for clue in selected_clues:
        st.write(f'**{clue["name"]}:** {clue["description"]}')
else:
    st.info("No clues selected for evidence review.")

st.caption(
    "The Bayesian engine uses manually specified likelihoods "
    "and assumes conditional independence between clues. "
    "Correlated evidence may produce misleading confidence."
)


# --------------------------------------------------
# 7. PLAYER ACCUSATION
# --------------------------------------------------

st.divider()
st.header("⚖️ Make Your Accusation")

st.write(
    "After reviewing the evidence, select the suspect you believe "
    "is responsible. You can change your decision as you investigate."
)

suspect_options = {
    suspect["name"]: suspect["id"]
    for suspect in suspects
}

with st.form("accusation_form"):
    selected_suspect_name = st.selectbox(
        "Who do you accuse?",
        options=list(suspect_options.keys()),
    )

    submitted = st.form_submit_button("Submit Accusation")

    if submitted:
        st.session_state.final_accusation = suspect_options[
            selected_suspect_name
        ]

if st.session_state.final_accusation:
    accused_id = st.session_state.final_accusation

    st.info(
        f"You accused {suspect_names[accused_id]}. "
        "Your decision has been recorded for this session."
    )

    if probabilities:
        current_leader = next(iter(probabilities))

        if accused_id == current_leader:
            st.write(
                "Your accusation matches the AI's current "
                "top-ranked hypothesis. This does not establish "
                "that the accusation is correct."
            )
        else:
            st.write(
                f'The AI currently ranks '
                f'{suspect_names[current_leader]} highest. '
                "Review the evidence before drawing a conclusion."
            )


# --------------------------------------------------
# 8. RESET THE INVESTIGATION
# --------------------------------------------------

st.divider()

if st.button("🔄 Restart Investigation"):
    st.session_state.discovered_clues = set()
    st.session_state.final_accusation = None

    for clue in clues:
        st.session_state.pop(f'clue_{clue["id"]}', None)

    st.rerun()


# --------------------------------------------------
# 9. FOOTER
# --------------------------------------------------

st.caption(
    "The Last Alibi | Core AI Project | Prototype Version 1.0"
)

import json
from pathlib import Path

import streamlit as st

from ai.logic_engine import check_contradictions, classify_contradiction
from ai.bayesian_engine import (
    calculate_suspect_probabilities,
    explain_probability_changes,
)

# --------------------------------------------------
# PAGE CONFIGURATION AND DATA
# --------------------------------------------------
st.set_page_config(
    page_title="The Last Alibi | Detective Bureau",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CASE_PATH = Path(__file__).parent / "case_data.json"
with CASE_PATH.open(encoding="utf-8") as file:
    case_data = json.load(file)

suspects = case_data["suspects"]
clues = case_data["clues"]
victim = case_data.get("victim", {})
incident = case_data.get("incident", {})
suspect_names = {suspect["id"]: suspect["name"] for suspect in suspects}

if "discovered_clues" not in st.session_state:
    st.session_state.discovered_clues = set()
if "final_accusation" not in st.session_state:
    st.session_state.final_accusation = None

# --------------------------------------------------
# PREMIUM DETECTIVE-NOIR UI
# --------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

    :root {
        --ink: #f5f0e8;
        --muted: #aaa6a0;
        --panel: #171719;
        --panel2: #1d1c1e;
        --line: rgba(236, 225, 208, .13);
        --red: #b84c50;
        --red-light: #e07a77;
        --gold: #c8a96b;
    }
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .stApp {
        background:
            radial-gradient(ellipse at 10% 0%, rgba(119, 35, 43, .18), transparent 35%),
            radial-gradient(ellipse at 90% 12%, rgba(153, 117, 58, .08), transparent 30%),
            #101012;
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: rgba(16,16,18,.82); }
    [data-testid="stToolbar"] { right: 1.5rem; }
    .block-container { max-width: 1320px; padding-top: 2.2rem; padding-bottom: 3rem; }
    h1, h2, h3 { letter-spacing: -.025em; color: var(--ink); }
    h1, h2 { font-family: 'Playfair Display', Georgia, serif !important; }
    h1 { font-size: clamp(2.5rem, 5vw, 4rem) !important; line-height: 1.05 !important; }
    h2 { font-size: 1.85rem !important; }
    h3 { font-size: 1.2rem !important; }
    p, li, label { color: #e7e1d8; }
    [data-testid="stCaptionContainer"] p { color: var(--muted); }
    hr { border-color: var(--line); margin: 2rem 0; }
    .eyebrow {
        font-family: 'DM Mono', monospace;
        color: var(--gold);
        font-size: .76rem;
        letter-spacing: .17em;
        text-transform: uppercase;
        margin-bottom: .7rem;
    }
    .hero {
        border: 1px solid rgba(200,169,107,.26);
        background: linear-gradient(125deg, rgba(42,26,29,.96), rgba(23,22,24,.96) 58%, rgba(30,27,22,.96));
        border-radius: 22px;
        padding: clamp(1.5rem, 4vw, 3.2rem);
        position: relative;
        overflow: hidden;
        margin: .4rem 0 1.5rem;
    }
    .hero:after {
        content: "CASE 001";
        position: absolute; right: 2rem; bottom: 1.1rem;
        font-family: 'DM Mono', monospace; font-size: clamp(2rem, 5vw, 4.4rem);
        letter-spacing: .1em; color: rgba(245,240,232,.035); font-weight: 500;
    }
    .hero-subtitle { color: #d3c5b6; font-size: 1.04rem; max-width: 760px; line-height: 1.75; }
    .hero-meta { color: var(--gold); font-family: 'DM Mono', monospace; font-size: .78rem; letter-spacing: .08em; margin-top: 1.3rem; }
    .section-kicker {
        font-family: 'DM Mono', monospace; text-transform: uppercase;
        letter-spacing: .13em; color: var(--red-light); font-size: .74rem;
        margin-bottom: .35rem;
    }
    .suspect-card {
        min-height: 255px; height: 100%; border: 1px solid var(--line);
        border-radius: 16px; padding: 1.2rem 1.2rem 1.15rem;
        background: linear-gradient(160deg, rgba(31,30,32,.96), rgba(20,20,22,.96));
        transition: border-color .2s ease, transform .2s ease;
    }
    .suspect-card:hover { border-color: rgba(200,169,107,.55); transform: translateY(-2px); }
    .suspect-number { color: var(--gold); font-family: 'DM Mono', monospace; font-size: .74rem; }
    .suspect-name { font-family: 'Playfair Display', Georgia, serif; font-size: 1.45rem; margin: .45rem 0 .15rem; color: var(--ink); }
    .suspect-role { color: var(--muted); font-size: .85rem; margin-bottom: 1.1rem; }
    .mini-label { color: var(--gold); font-family: 'DM Mono', monospace; text-transform: uppercase; font-size: .68rem; letter-spacing: .1em; margin-top: .65rem; }
    .mini-value { color: #e8e0d5; font-size: .91rem; line-height: 1.5; }
    .metric-card {
        background: rgba(28,27,29,.8); border: 1px solid var(--line);
        border-radius: 14px; padding: 1.05rem 1.2rem;
    }
    .metric-label { color: var(--muted); font-family: 'DM Mono', monospace; font-size: .72rem; text-transform: uppercase; letter-spacing: .1em; }
    .metric-value { color: var(--ink); font-family: 'Playfair Display', Georgia, serif; font-size: 2rem; margin-top: .25rem; }
    .clue-card {
        border: 1px solid var(--line); background: rgba(25,24,26,.88);
        border-radius: 14px; padding: 1rem 1.1rem; margin-bottom: .6rem;
    }
    .clue-card-selected { border-color: rgba(184,76,80,.7); background: linear-gradient(110deg, rgba(73,30,34,.55), rgba(25,24,26,.92)); }
    .clue-tag {
        display: inline-block; border: 1px solid rgba(200,169,107,.35); color: var(--gold);
        border-radius: 999px; padding: .2rem .55rem; font-family: 'DM Mono', monospace;
        font-size: .67rem; letter-spacing: .05em; text-transform: uppercase;
    }
    .result-card {
        border: 1px solid var(--line); background: linear-gradient(145deg, #1d1c1e, #151517);
        border-radius: 15px; padding: 1.05rem 1.2rem; margin-bottom: .7rem;
    }
    .result-top { display:flex; align-items:center; justify-content:space-between; gap:1rem; margin-bottom:.6rem; }
    .result-name { color: var(--ink); font-weight: 700; font-size: 1rem; }
    .result-pct { color: var(--gold); font-family: 'DM Mono', monospace; font-size: 1rem; }
    .rank-pill { color: var(--red-light); font-family: 'DM Mono', monospace; font-size: .72rem; margin-right: .6rem; }
    .notice {
        border-radius: 12px; border: 1px solid rgba(200,169,107,.3);
        background: rgba(200,169,107,.08); padding: .9rem 1rem; color: #e7d9b9;
        margin: .7rem 0 1rem; line-height: 1.55;
    }
    .notice-red { border-color: rgba(184,76,80,.42); background: rgba(184,76,80,.1); color: #f0c7c4; }
    .footer {
        border-top: 1px solid var(--line); margin-top: 3rem; padding-top: 1.2rem;
        color: #8e8984; font-family: 'DM Mono', monospace; font-size: .72rem;
        display:flex; justify-content:space-between; gap:1rem; flex-wrap:wrap;
    }
    div[data-testid="stButton"] button, div[data-testid="stFormSubmitButton"] button {
        border-radius: 10px; border: 1px solid rgba(200,169,107,.4);
        background: linear-gradient(135deg, #8f373d, #6d282e);
        color: #fff4e9; font-weight: 700; padding: .55rem 1.1rem;
        transition: all .2s ease;
    }
    div[data-testid="stButton"] button:hover, div[data-testid="stFormSubmitButton"] button:hover {
        border-color: var(--gold); background: linear-gradient(135deg, #a94449, #823138);
        color: white; transform: translateY(-1px);
    }
    [data-testid="stCheckbox"] label { color: #e7e1d8; }
    [data-testid="stExpander"] {
        border: 1px solid var(--line); border-radius: 12px; background: rgba(25,24,26,.65);
    }
    [data-testid="stProgress"] > div > div { background: linear-gradient(90deg, #8e343a, #c8a96b); }
    div[data-testid="stMetric"] {
        background: rgba(28,27,29,.8); border: 1px solid var(--line);
        border-radius: 14px; padding: 1rem 1.1rem;
    }
    div[data-testid="stMetricLabel"] { color: var(--muted); }
    div[data-testid="stMetricValue"] { color: var(--ink); font-family: 'Playfair Display', Georgia, serif; }
    .stSelectbox [data-baseweb="select"] > div { background-color: #201f21; border-color: var(--line); }
    @media (max-width: 700px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; }
        .hero:after { display: none; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def section_header(kicker, title, description=None):
    st.markdown(
        f'<div class="section-kicker">{kicker}</div><h2 style="margin-top:0">{title}</h2>',
        unsafe_allow_html=True,
    )
    if description:
        st.markdown(f'<p style="color:#aaa6a0;margin-top:-.35rem;margin-bottom:1.1rem">{description}</p>', unsafe_allow_html=True)

# --------------------------------------------------
# HERO / CASE SUMMARY
# --------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
      <div class="eyebrow">The Blackwood Files &nbsp; / &nbsp; Active Investigation</div>
      <h1>THE LAST ALIBI</h1>
      <div style="font-family:'Playfair Display',Georgia,serif;font-size:1.4rem;color:#e7d9c7;margin:.75rem 0 1rem">
        The Midnight at Blackwood Manor
      </div>
      <div class="hero-subtitle">
        Richard Blackwood has been found dead in his study. Four suspects. Conflicting stories.
        One timeline that does not quite add up. Examine the evidence and let the reasoning engine
        help you determine which explanation is best supported.
      </div>
      <div class="hero-meta">CASE NO. BW-001 &nbsp; • &nbsp; VICTIM: {victim.get("name", "Richard Blackwood")} &nbsp; • &nbsp; LOCATION: {incident.get("location", "Blackwood Manor")}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

metric1, metric2, metric3 = st.columns(3)
metric1.metric("Suspects under review", len(suspects))
metric2.metric("Evidence collected", len(st.session_state.discovered_clues))
metric3.metric("Evidence in case file", len(clues))

st.markdown("<br>", unsafe_allow_html=True)

# --------------------------------------------------
# SUSPECT BOARD
# --------------------------------------------------
section_header("01 / Persons of interest", "The suspect board", "Every suspect has a motive. Every alibi deserves scrutiny.")
suspect_columns = st.columns(4)
for index, (column, suspect) in enumerate(zip(suspect_columns, suspects), start=1):
    with column:
        st.markdown(
            f"""
            <div class="suspect-card">
              <div class="suspect-number">PERSON OF INTEREST / {index:02d}</div>
              <div class="suspect-name">{suspect["name"]}</div>
              <div class="suspect-role">{suspect["role"]}</div>
              <div class="mini-label">Possible motive</div>
              <div class="mini-value">{suspect["motive"]}</div>
              <div class="mini-label">Claimed location</div>
              <div class="mini-value">{suspect["alibi"]["location"]} · {suspect["alibi"]["start"]}–{suspect["alibi"]["end"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# --------------------------------------------------
# EVIDENCE ROOM
# --------------------------------------------------
section_header(
    "02 / Evidence locker",
    "The investigation room",
    "Select the clues you have uncovered. The AI uses only selected clues to update its analysis.",
)
st.markdown(
    '<div class="notice">FIELD NOTE &nbsp; / &nbsp; Evidence is not all equally informative. Start with what you know, then watch how each discovery changes the picture.</div>',
    unsafe_allow_html=True,
)

selected_clue_ids = set()
clue_columns = st.columns(2)
for index, clue in enumerate(clues):
    with clue_columns[index % 2]:
        is_selected_before = clue["id"] in st.session_state.discovered_clues
        with st.container(border=True):
            head_col, toggle_col = st.columns([4, 1])
            with head_col:
                st.markdown(f'<span class="clue-tag">{clue["type"].replace("_", " ")}</span>', unsafe_allow_html=True)
                st.markdown(f"### {clue['name']}")
            with toggle_col:
                is_discovered = st.checkbox(
                    "Collected",
                    value=is_selected_before,
                    key=f'clue_{clue["id"]}',
                )
            st.write(clue["description"])
            if is_discovered:
                st.caption("✓ Evidence collected and included in current analysis")
                selected_clue_ids.add(clue["id"])
            else:
                st.caption("Not yet collected")

st.session_state.discovered_clues = selected_clue_ids

st.divider()

# --------------------------------------------------
# AI RESULTS
# --------------------------------------------------
section_header("03 / Analysis desk", "AI investigation results", "Bayesian probability estimates and rule-based contradiction checks.")
probabilities = {}
if selected_clue_ids:
    probabilities = calculate_suspect_probabilities(case_data, discovered_clue_ids=selected_clue_ids)

if not selected_clue_ids:
    st.markdown(
        '<div class="notice notice-red"><strong>Evidence status: Empty case file.</strong><br>No clues have been collected. Suspects retain equal prior probability; any displayed order would be a tie-break, not a meaningful ranking.</div>',
        unsafe_allow_html=True,
    )
elif len(selected_clue_ids) < 3:
    st.markdown(
        f'<div class="notice"><strong>Evidence status: Preliminary.</strong><br>{len(selected_clue_ids)} clue(s) collected. Treat the current ranking as provisional and investigate further.</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="notice"><strong>Evidence status: Under review.</strong><br>{len(selected_clue_ids)} clues collected. Compare the ranking with the logical checks before making an accusation.</div>',
        unsafe_allow_html=True,
    )

ranking_col, logic_col = st.columns([1.15, 1])
with ranking_col:
    st.markdown("### Suspect probability ranking")
    st.caption("Model-based estimates from configured priors and clue likelihoods—not verified probabilities of real-world guilt.")
    if probabilities:
        for rank, (suspect_id, probability) in enumerate(probabilities.items(), start=1):
            name = suspect_names[suspect_id]
            st.markdown(
                f'<div class="result-card"><div class="result-top"><div class="result-name"><span class="rank-pill">#{rank:02d}</span>{name}</div><div class="result-pct">{probability:.1%}</div></div>',
                unsafe_allow_html=True,
            )
            st.progress(float(max(0.0, min(1.0, probability))))
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Collect a clue to activate the probability ranking.")

with logic_col:
    st.markdown("### Logical reasoning")
    contradictions = check_contradictions(case_data, discovered_clue_ids=selected_clue_ids)
    if contradictions:
        st.markdown(
            f'<div class="notice notice-red"><strong>{len(contradictions)} potential contradiction(s)</strong><br>One or more observations may conflict with a suspect’s stated alibi.</div>',
            unsafe_allow_html=True,
        )
        for contradiction in contradictions:
            classification = classify_contradiction(contradiction)
            with st.expander(f'{classification["level"]} · {contradiction["suspect_name"]} / {contradiction["clue_name"]}'):
                st.write(contradiction["explanation"])
                st.write(f'**Observation confidence:** {classification["confidence"]:.0%}')
                st.write(f'**Assessment:** {classification["explanation"]}')
                st.caption("A contradiction is a reason to investigate further, not proof of guilt.")
    else:
        st.info("No potential alibi contradictions were detected in the selected evidence.")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### Explainable AI / Why this ranking?")
if selected_clue_ids:
    explanations = explain_probability_changes(case_data, selected_clue_ids)
    st.caption("Each explanation describes how evidence changes the model's estimates. It does not prove guilt.")
    if explanations:
        for result in explanations:
            with st.expander(result["clue_name"]):
                for change in result["changes"]:
                    st.markdown(f"**{change['suspect_name']}**")
                    st.write(change["explanation"])
                    st.progress(float(max(0.0, min(1.0, change["after"]))))
    else:
        st.info("No explanation is available for the selected evidence.")
else:
    st.info("Collect one or more clues to see how evidence affects the estimates.")

with st.expander("Evidence review / collected clues"):
    selected_clues = [clue for clue in clues if clue["id"] in selected_clue_ids]
    if selected_clues:
        for clue in selected_clues:
            st.markdown(f"**{clue['name']}** · {clue['description']}")
    else:
        st.info("No clues have been collected yet.")
    st.caption("The Bayesian engine uses manually specified likelihoods and assumes conditional independence between clues. Correlated evidence may produce misleading confidence.")

st.divider()

# --------------------------------------------------
# ACCUSATION
# --------------------------------------------------
section_header("04 / Your verdict", "Make your accusation", "You are the investigator. Review the evidence, then record your conclusion.")
suspect_options = {suspect["name"]: suspect["id"] for suspect in suspects}
with st.container(border=True):
    st.markdown("### Who do you believe is responsible?")
    with st.form("accusation_form"):
        selected_suspect_name = st.selectbox("Select a suspect", options=list(suspect_options.keys()))
        submitted = st.form_submit_button("Record accusation")
        if submitted:
            st.session_state.final_accusation = suspect_options[selected_suspect_name]

if st.session_state.final_accusation:
    accused_id = st.session_state.final_accusation
    st.markdown(
        f'<div class="notice"><strong>Accusation recorded:</strong> {suspect_names[accused_id]}. Your decision is saved for this session.</div>',
        unsafe_allow_html=True,
    )
    if probabilities:
        current_leader = next(iter(probabilities))
        if accused_id == current_leader:
            st.write("Your accusation matches the AI's current top-ranked hypothesis. This does not establish that the accusation is correct.")
        else:
            st.write(f"The AI currently ranks {suspect_names[current_leader]} highest. Consider reviewing the evidence before drawing a conclusion.")

reset_col, note_col = st.columns([1, 3])
with reset_col:
    if st.button("↺ Restart investigation"):
        st.session_state.discovered_clues = set()
        st.session_state.final_accusation = None
        for clue in clues:
            st.session_state.pop(f'clue_{clue["id"]}', None)
        st.rerun()
with note_col:
    st.caption("Reset clears collected clues and your accusation for a fresh investigation.")

st.markdown(
    """
    <div class="footer">
      <span>THE LAST ALIBI · CORE AI PROJECT · PROTOTYPE 1.1</span>
      <span>FICTIONAL CASEWORK / DECISIONS REQUIRE HUMAN JUDGMENT</span>
    </div>
    """,
    unsafe_allow_html=True,
)

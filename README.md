# The Last Alibi
### An Explainable AI-Powered Mystery Detective Game

**The Last Alibi** is a Python-based mystery investigation game in which players examine evidence, investigate suspects, identify contradictions in alibis, and make an accusation. It combines Bayesian probability estimation with rule-based logical reasoning to make its conclusions more transparent.

## Project Objectives

- Develop an interactive mystery investigation experience.
- Rank suspects using Bayesian probability updates.
- Detect potential contradictions between suspect alibis and discovered evidence.
- Explain how clues influence suspect rankings.
- Evaluate model behavior across multiple fictional cases and evidence combinations.

## Key Features

- **Interactive investigation:** Explore suspects and discover clues.
- **Bayesian suspect ranking:** Estimate relative suspect probabilities using clue likelihoods.
- **Explainable results:** Trace how evidence changes the rankings.
- **Contradiction detection:** Flag evidence that conflicts with a suspect's stated alibi.
- **Evidence sufficiency indicator:** Distinguish preliminary conclusions from results based on more evidence.
- **Multi-case evaluation:** Test the model across four fictional mysteries.
- **Automated tests:** Validate case data, probability calculations, logic rules, and robustness.

## Technology Stack

- Python
- Streamlit
- Bayesian probability calculations
- Rule-based logical reasoning
- JSON for case data
- Pytest for automated testing

## Project Structure

```text
The Last Alibi/
├── app.py
├── case_data.json
├── requirements.txt
├── README.md
├── ai/
│   ├── __init__.py
│   ├── bayesian_engine.py
│   └── logic_engine.py
├── cases/
│   ├── ashford_station.json
│   ├── observatory.json
│   └── grand_hotel.json
├── tests/
│   ├── test_case_data.py
│   ├── test_logic_engine.py
│   ├── test_bayesian_engine.py
│   └── test_ai_robustness.py
└── evaluation/
    ├── ground_truth.json
    ├── cross_case_evaluation.py
    ├── reliability_experiment.py
    ├── exhaustive_model_comparison.py
    ├── macro_average_comparison.py
    └── FINAL_EVALUATION_REPORT.md
```

*The structure above highlights the main files; additional evaluation scripts and case-specific ground-truth files are also included.*

## Installation and Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd "The Last Alibi"
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Launch the application

```bash
streamlit run app.py
```

Streamlit will display a local URL in your terminal. Open that URL in your browser.

## Running Tests

Run the automated test suite from the project root:

```bash
python -m pytest -v
```

The previously recorded test run passed 19 tests. Re-run the command to verify the current version.

## AI Architecture

### Bayesian Reasoning Engine

The Bayesian engine uses manually specified clue likelihoods to update suspect probabilities. It supports evaluating all available clues or a selected subset of discovered clues.

### Logical Contradiction Engine

The logic engine checks whether sufficiently confident observations conflict with a suspect's claimed alibi during the incident time window.

### Explainability

The application shows how evidence affects suspect rankings and highlights potential contradictions. These outputs support investigation; they do not independently establish guilt.

## Evaluation

The project compares the original Bayesian model with an experimental reliability-adjusted model across four fictional cases.

In the exhaustive evidence-subset experiment, the original model achieved:

- **Top-1 accuracy:** 95.31%
- **Mean reciprocal rank:** 0.9739
- **Mean culprit probability:** 72.63%
- **Mean log loss:** 0.3716

In the equal-weight, case-balanced macro-average experiment, the original model achieved:

- **Top-1 accuracy:** 81.14%
- **Mean reciprocal rank:** 0.8936
- **Mean culprit probability:** 53.89%
- **Mean log loss:** 0.7091

These results come from four manually authored cases and their predefined ground truths. Evidence subsets are not independent cases, and the likelihoods are illustrative assumptions rather than empirically trained or calibrated estimates. The results should not be interpreted as real-world detective accuracy.

See `evaluation/FINAL_EVALUATION_REPORT.md` for the full methodology, comparisons, sensitivity analysis, and limitations.

## Limitations

- Clue likelihoods are manually authored.
- The Bayesian model assumes conditional independence between clues, which may overstate confidence when clues are correlated.
- The four fictional cases provide limited evidence of generalization.
- Contradiction severity thresholds are rule-based and have not been empirically validated.
- Suspect probabilities are model estimates, not proof of guilt.

## Future Scope

- Add more independently authored mystery cases.
- Calibrate likelihoods using a defined data-generation and validation protocol.
- Investigate methods for handling correlated evidence.
- Improve the visual investigation interface.
- Add evidence timelines, richer interrogation mechanics, and further robustness tests.

## Team Contributions

Add each team member's name and their actual contribution to the project here.

## Disclaimer

The Last Alibi is an educational and experimental project. Its fictional investigations and AI-generated rankings are intended for gameplay and demonstration, not real-world criminal investigations.

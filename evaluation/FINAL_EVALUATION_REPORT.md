# The Last Alibi — AI Evaluation Report

## 1. Objective

The objective of this experiment was to evaluate a Bayesian suspect-ranking engine across four manually authored fictional mystery cases. The experiment compared the original Bayesian model with a reliability-adjusted variant.

## 2. Experimental Setup

The evaluation used four cases:

- The Midnight at Blackwood Manor
- The Last Train to Ashford
- The Observatory at 11:47
- The Vanishing at the Grand Hotel

Each case contained four suspects and a predefined culprit. Suspect-specific clue likelihoods and clue reliability scores were manually authored.

All non-empty subsets of each case's clues were evaluated. This produced 4,860 evidence combinations per model:

- Blackwood Manor: 4,095 combinations
- Ashford Station: 255 combinations
- Observatory: 255 combinations
- Grand Hotel: 255 combinations

The combinations are related evidence subsets within four cases, not independent mystery cases.

## 3. Evaluation Metrics

- **Top-1 accuracy:** proportion of evidence combinations where the predefined culprit ranked first.
- **Mean Reciprocal Rank (MRR):** measures how highly the predefined culprit is ranked.
- **Mean culprit probability:** average probability assigned to the predefined culprit.
- **Log loss:** penalizes low probability assigned to the predefined culprit. Lower values are better.

A uniform baseline assigns probability 0.25 to each of the four suspects, giving a log loss of approximately 1.3863.

## 4. Case-Balanced Results

| Metric | Original Model | Reliability-Adjusted Model |
|---|---:|---:|
| Macro top-1 accuracy | 81.14% | 77.89% |
| Macro MRR | 0.8936 | 0.8770 |
| Mean culprit probability | 53.89% | 49.27% |
| Mean log loss | 0.7091 | 0.8005 |

The macro-average gives each mystery equal weight, avoiding domination of the aggregate result by Blackwood Manor, which has more clues than the other cases.

## 5. Results by Case

| Case | Original Top-1 Accuracy | Adjusted Top-1 Accuracy |
|---|---:|---:|
| Blackwood Manor | 99.07% | 99.00% |
| Ashford Station | 94.90% | 94.90% |
| Observatory | 85.49% | 83.92% |
| Grand Hotel | 45.10% | 33.73% |

The Grand Hotel case exposed a significant weakness. The original model ranked the predefined culprit first in only 45.10% of its non-empty evidence combinations. This indicates that the model's performance depends strongly on the evidence pattern and the manually authored likelihood assumptions.

## 6. Reliability Adjustment Experiment

The experimental variant adjusted each suspect's likelihood toward the mean likelihood for that clue, using the clue's manually assigned reliability score.

The reliability-adjusted model performed worse on the macro-averaged metrics. Its top-1 accuracy was 77.89%, compared with 81.14% for the original model, and its mean log loss was higher.

The original model is therefore retained as the current baseline. These findings do not establish that reliability adjustment is universally inferior; the reliability scores were manually specified, and only four fictional cases were evaluated.

## 7. Sensitivity Analysis

A leave-one-clue-out experiment was conducted for the Grand Hotel case. Removing individual clues changed the predefined culprit's probability and, in some cases, changed the top-ranked suspect.

This demonstrates that individual clues can substantially affect the ranking. Adding more evidence does not guarantee that the predefined culprit's probability will increase.

## 8. Limitations

1. Only four fictional mystery cases were used.
2. The ground-truth culprits and likelihood assumptions were manually authored.
3. The evidence subsets are not independent test cases.
4. The reliability scores were not empirically calibrated.
5. The Bayesian model relies on simplifying assumptions, including combining clue likelihoods as if they were conditionally independent.
6. A high suspect probability does not establish guilt; it reflects the model's assumptions and supplied evidence.

## 9. Conclusion

The original Bayesian model outperformed the reliability-adjusted variant in the case-balanced evaluation. However, performance varied substantially across cases, especially for the Grand Hotel mystery.

The experiments support retaining the original model as the baseline while investigating evidence sensitivity, likelihood calibration, and performance on additional independently designed cases. The results should be interpreted as controlled evidence-space analysis rather than evidence of real-world detective accuracy.
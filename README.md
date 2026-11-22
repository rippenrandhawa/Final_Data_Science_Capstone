# Final Data Science Capstone Project

## Leakage-Aware Term-Deposit Campaign Targeting

A complete, reproducible capstone that defines a real business problem, prepares a
reliable public dataset, compares machine-learning models, evaluates a selected solution
on a chronological holdout, analyses errors and drift, and translates the evidence into
responsible business recommendations.

## Business problem

Outbound calls consume agent time and customer attention. The bank needs a **pre-call
ranking system** that prioritises clients with a higher likelihood of subscribing to a
term deposit. The system must use only information available before the call and must
not automatically exclude clients.

## Objectives and success criteria

1. Clean and validate real campaign data.
2. Engineer prediction-time-safe features.
3. Compare logistic regression, random forest and histogram gradient boosting.
4. Use chronological train/validation/test splits.
5. Beat a prevalence baseline on ROC-AUC, PR-AUC and top-20% lift.
6. Quantify false positives, false negatives, drift and subgroup performance.
7. Recommend a controlled pilot and measurable governance process.

## Dataset

**UCI Bank Marketing**, DOI [10.24432/C5K306](https://doi.org/10.24432/C5K306),
CC BY 4.0. The project uses `bank-additional-full.csv`: 41,188 records, 20 inputs,
ordered by date from May 2008 to November 2010.

The target is whether the client subscribed to a term deposit. The data describes a
Portuguese bank and is historical; transfer to another market or current campaign
requires new validation.

## Critical leakage control

Call `duration` is known only after the call ends. It is **excluded** from every
pre-call deployable model. A separate duration-inclusive diagnostic model is included
only to show how leakage inflates apparent performance.

## Methodology

1. Preserve the original UCI archive, metadata and CSV.
2. Audit dimensions, duplicates, physical nulls and semantic `unknown` values.
3. Engineer previous-contact, contact-pressure, obligation and quality features.
4. Split sequentially: first 70% train, next 15% validation, final 15% test.
5. Select the model using validation PR-AUC.
6. Tune the classification threshold on validation only.
7. Evaluate once on the untouched chronological test set.
8. Analyse ranking lift, errors, permutation importance and age-band metrics.
9. Document limitations and define a responsible pilot roadmap.

## Verified results

| Metric | Held-out result |
|---|---:|
| Selected model | Histogram gradient boosting |
| Test ROC-AUC | 0.635 |
| Test PR-AUC | 0.513 |
| Validation-tuned precision | 0.508 |
| Validation-tuned recall | 0.558 |
| Validation-tuned F1 | 0.532 |
| Top-20% lift | 1.35× |
| Top-20% subscriber capture | 639 of 2,376 (26.89%) |

### Dominant model risk: temporal drift

| Split | Positive rate |
|---|---:|
| Train | 5.57% |
| Validation | 10.65% |
| Test | 38.45% |

The model ranks better than random, but the changing base rate makes absolute
probabilities and fixed thresholds unstable. The result supports a **controlled pilot**,
not a production deployment claim.

## Key insights

- Previous campaign success is strongly associated with current subscription.
- Cellular-contact records convert more often than telephone records, but channel
  selection may confound the relationship.
- More current-campaign contacts are negatively associated with subscription.
- Top-scored 20% of test records contain 26.89% of subscribers.
- Precision, recall, selection and false-positive rates vary by age band.
- Adding post-call duration raises apparent ROC-AUC from 0.635 to 0.697, illustrating
  leakage—not a valid performance gain.

## Recommendations

### High priority

- Use the model only as a ranked pilot against a random eligible control.
- Monitor prevalence, PR-AUC, Brier score and score distribution every campaign.
- Choose the threshold using contact cost, expected contribution and capacity.
- Enforce a prediction-time feature contract that bans post-call fields.
- Complete legal, consent, fairness and human-override reviews.

### Medium priority

- Test contact channel and cadence through controlled experiments.
- Develop a consent-aware re-engagement strategy for prior successful responders.

### Long term

- Add anonymised client IDs, explicit timestamps, offer details, contact cost,
  deposit contribution, consent and complaint outcomes.
- Explore calibrated models and uplift modelling after a randomised campaign.

## Project structure

```text
Final_Data_Science_Capstone/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                         # UCI archives, names file and original CSV
│   └── processed/
│       └── bank_marketing_cleaned.csv
├── notebooks/
│   └── Final_Data_Science_Capstone.ipynb
├── scripts/
│   └── capstone_analysis.py
├── models/
│   └── term_deposit_targeting_model.joblib
├── outputs/
│   ├── charts/                      # 13 PNGs at 200 DPI
│   ├── tables/                      # metrics, predictions, audits, recommendations
│   └── summaries/                   # quality, model, statistics, QA
├── report/
│   └── Final_Data_Science_Capstone_Report.docx
├── presentation/
│   └── Final_Data_Science_Capstone_Presentation.pptx
├── references/
│   └── dataset_source.md
└── build/                           # notebook, report, presentation and QA builders
```

## Reproduce the project

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts\capstone_analysis.py
python build\build_documentation.py
python build\build_notebook.py
python build\build_report.py
python build\build_presentation.py
python build\qa_project.py
```

The analysis uses `random_state=42`, relative paths and an explicit sequential split.

## Deliverables

- Executed 27-cell Jupyter notebook with zero errors
- Fitted scikit-learn pipeline (`.joblib`)
- Cleaned dataset and data dictionary
- 13 charts at 200 DPI
- Model comparisons, test predictions, gains, errors and age-band audit
- Professional Word report
- 12-slide executive presentation
- QA report and file-hash manifest
- Complete ZIP archive

## Limitations

- Strong temporal drift and poor probability stability
- No client ID for grouped splitting
- Historic Portuguese data with limited geographic/current validity
- No contact cost or deposit contribution for profit optimisation
- Observational data cannot establish causal campaign effects
- Incomplete fairness assessment
- Prototype is not authorised for autonomous targeting

## References

1. Moro, S., Rita, P., & Cortez, P. (2014). *Bank Marketing* [Dataset]. UCI Machine
   Learning Repository. <https://doi.org/10.24432/C5K306>
2. Moro, S., Cortez, P., & Rita, P. (2014). A data-driven approach to predict the
   success of bank telemarketing. *Decision Support Systems*, 62, 22–31.
3. scikit-learn documentation: <https://scikit-learn.org/stable/>

# Executive Summary

This capstone builds a leakage-aware model to rank term-deposit prospects before an
outbound call. It uses 41,188 chronologically ordered records from UCI Bank Marketing.
The selected histogram gradient boosting model excludes call duration because duration
is unavailable before the call.

## Held-out results

- ROC-AUC: **0.635**
- PR-AUC: **0.513** against a 38.45% test prevalence
- Validation-tuned precision: **0.508**
- Validation-tuned recall: **0.558**
- Validation-tuned F1: **0.532**
- Top-20% lift: **1.35×**
- Subscribers captured in the top 20%: **639 of 2,376**

The model is better than random but not production-ready. The target prevalence moves
from 5.57% in training to 10.65% in validation and 38.45% in test, revealing strong
temporal drift and calibration risk. The recommended next step is a controlled current-
data pilot with economic thresholding, consent/legal review, drift and subgroup
monitoring, and human oversight—not autonomous targeting.

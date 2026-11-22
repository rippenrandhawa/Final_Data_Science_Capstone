# Dataset Source

- **Name:** Bank Marketing
- **Repository:** UCI Machine Learning Repository, dataset 222
- **DOI:** <https://doi.org/10.24432/C5K306>
- **Dataset page:** <https://archive.ics.uci.edu/dataset/222/bank+marketing>
- **Creators:** S. Moro, P. Rita and P. Cortez
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **File used:** `bank-additional-full.csv`
- **Instances:** 41,188
- **Inputs:** 20
- **Period:** May 2008–November 2010
- **Order:** Date-ordered, according to UCI
- **Task:** Predict whether a client subscribes to a term deposit.

## Citation

Moro, S., Rita, P., & Cortez, P. (2014). *Bank Marketing* [Dataset]. UCI Machine
Learning Repository. https://doi.org/10.24432/C5K306

Moro, S., Cortez, P., & Rita, P. (2014). A data-driven approach to predict the
success of bank telemarketing. *Decision Support Systems*, 62, 22–31.

## Prediction-time caveat

`duration` is the length of the last contact and is only known after the call ends.
It is therefore excluded from the pre-call deployable model. The project includes a
separate duration-inclusive diagnostic model only to demonstrate leakage inflation.

"""Build and execute the capstone notebook from verified outputs."""
from pathlib import Path
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'notebooks/Final_Data_Science_Capstone.ipynb'
def md(x):return nbformat.v4.new_markdown_cell(x)
def code(x):return nbformat.v4.new_code_cell(x.strip())
nb=nbformat.v4.new_notebook(metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.13'}})
nb.cells=[
md('# Final Data Science Capstone Project\n## Leakage-Aware Term-Deposit Campaign Targeting\n\n**Business problem:** rank clients by pre-call subscription likelihood so a campaign manager can allocate limited outbound-call capacity more efficiently.\n\n**Source:** UCI Bank Marketing, `bank-additional-full.csv`, 41,188 date-ordered records from Portuguese bank campaigns, May 2008–November 2010. DOI: [10.24432/C5K306](https://doi.org/10.24432/C5K306), CC BY 4.0.'),
md('## 1. Scope and prediction contract\nThe prediction is made **before the call**. Call `duration` is known only after the call ends and is excluded from the deployable model. The project is a ranking prototype, not an autonomous decision system.'),
code('''from pathlib import Path
import json, joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.metrics import *
from IPython.display import display, Image
ROOT=Path('..')
RAW=ROOT/'data/raw/bank-additional/bank-additional-full.csv'
CLEAN=ROOT/'data/processed/bank_marketing_cleaned.csv'
pd.set_option('display.float_format',lambda v:f'{v:,.4f}')
print('pandas',pd.__version__,'numpy',np.__version__)'''),
md('## 2. Raw-data inspection'),
code('''raw=pd.read_csv(RAW,sep=';')
print(f'Raw dimensions: {raw.shape[0]:,} rows × {raw.shape[1]} columns')
print('Exact duplicates:',raw.duplicated().sum())
print('Null cells:',raw.isna().sum().sum())
print('Semantic unknown values:',(raw.select_dtypes('object')=='unknown').sum().sum())
display(raw.head())'''),
md('## 3. Cleaned data and engineered features\nUnknown categories are retained as information rather than treated as null. `pdays=999` is converted into a missing `days_since_previous` plus an explicit previously-contacted flag. Outliers are not removed automatically.'),
code('''df=pd.read_csv(CLEAN)
print(f'Clean dimensions: {df.shape[0]:,} rows × {df.shape[1]} columns')
print('Subscription rate:',f'{df.subscribed.mean():.2%}')
display(df[['age','job','campaign','pdays','previously_contacted','contact_pressure','subscribed']].head())'''),
md('## 4. Exploratory analysis'),
code('''display(pd.read_csv(ROOT/'outputs/tables/segment_conversion_rates.csv').query("feature in ['job','contact','poutcome']").sort_values(['feature','conversion_rate'],ascending=[True,False]).groupby('feature').head(6))'''),
code('''display(Image(filename=str(ROOT/'outputs/charts/01_target_balance.png')))
display(Image(filename=str(ROOT/'outputs/charts/03_job_conversion.png')))
display(Image(filename=str(ROOT/'outputs/charts/04_previous_outcome.png')))'''),
md('## 5. Leakage-aware temporal evaluation\nThe source is ordered by date. The first 70% is training, the next 15% validation and the final 15% test. This is harder and more realistic than random shuffling because campaign conditions change over time.'),
code('''splits=pd.read_csv(ROOT/'outputs/tables/split_summary.csv'); display(splits)
print('The sharp prevalence shift is a model-risk finding, not a preprocessing error.')'''),
md('## 6. Model comparison\nThree deployable candidates are compared on the chronological validation set: class-weighted logistic regression, random forest and histogram gradient boosting. PR-AUC is the primary selection metric because the validation target is imbalanced.'),
code('''val=pd.read_csv(ROOT/'outputs/tables/validation_model_comparison.csv'); display(val[['model','roc_auc','pr_auc','precision','recall','f1','top20_lift']])
display(Image(filename=str(ROOT/'outputs/charts/06_model_comparison.png')))'''),
md('## 7. Held-out test performance'),
code('''summary=json.loads((ROOT/'outputs/summaries/model_summary.json').read_text())
test=pd.read_csv(ROOT/'outputs/tables/test_model_performance.csv')
display(test[['model','threshold','roc_auc','pr_auc','precision','recall','f1','brier','top20_lift']])
print(json.dumps(summary,indent=2))'''),
code('''display(Image(filename=str(ROOT/'outputs/charts/07_roc_pr_curves.png')))
display(Image(filename=str(ROOT/'outputs/charts/08_confusion_matrix.png')))
display(Image(filename=str(ROOT/'outputs/charts/09_cumulative_gains.png')))'''),
md('## 8. Leakage demonstration\nThe duration-inclusive model is diagnostic only. Its better score demonstrates how a realistic-looking model can be invalid at the actual decision point.'),
code('''display(pd.read_csv(ROOT/'outputs/tables/leakage_demonstration.csv'))
display(Image(filename=str(ROOT/'outputs/charts/12_leakage_demo.png')))'''),
md('## 9. Explainability and error analysis'),
code('''imp=pd.read_csv(ROOT/'outputs/tables/permutation_importance.csv'); display(imp.head(12))
display(Image(filename=str(ROOT/'outputs/charts/10_feature_importance.png')))'''),
code('''scored=pd.read_csv(ROOT/'outputs/tables/test_scored_predictions.csv')
print(scored.error_type.value_counts())
display(pd.read_csv(ROOT/'outputs/tables/age_band_model_audit.csv'))
display(Image(filename=str(ROOT/'outputs/charts/13_age_band_audit.png')))'''),
md('## 10. Statistical observations\nPrevious campaign outcome is associated with subscription (chi-square p < 0.001). Current campaign contact count is negatively associated with subscription, but neither relationship proves a causal intervention effect.'),
code('''tests=json.loads((ROOT/'outputs/summaries/statistical_tests.json').read_text()); print(json.dumps(tests,indent=2))'''),
md('## 11. Insights and recommendations'),
code('''display(pd.read_csv(ROOT/'outputs/tables/insights_table.csv'))
display(pd.read_csv(ROOT/'outputs/tables/recommendation_matrix.csv')[['recommendation','priority','success_kpi']])'''),
md('## 12. Limitations and future scope\n- Strong temporal drift and poor absolute calibration.\n- No client ID, so repeated clients cannot be grouped across splits.\n- Historic Portuguese data may not generalise to another country or current campaigns.\n- Observational associations are not causal effects.\n- Age-band audit is not a complete fairness assessment.\n- Deployment requires consent, legal review, monitoring, economic thresholding and a current pilot.\n\n**Conclusion:** the model is suitable for a controlled ranking pilot, not autonomous production use.')]
OUT.parent.mkdir(parents=True,exist_ok=True); client=NotebookClient(nb,timeout=900,kernel_name='python3',resources={'metadata':{'path':str(OUT.parent)}});client.execute();nbformat.write(nb,OUT)
errs=[o for c in nb.cells if c.cell_type=='code' for o in c.get('outputs',[]) if o.output_type=='error'];print('written',OUT,'cells',len(nb.cells),'code',sum(c.cell_type=='code' for c in nb.cells),'errors',len(errs))

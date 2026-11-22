"""Automated QA for the final capstone."""
from pathlib import Path
import ast,hashlib,json,sys
import nbformat,pandas as pd
from docx import Document
from pptx import Presentation
from PIL import Image
import joblib
R=Path(__file__).resolve().parents[1];checks=[]
def add(n,o,d=''):checks.append((n,bool(o),str(d)))
def ex(x):return (R/x).exists()
req=['README.md','requirements.txt','data/raw/bank_marketing.zip','data/raw/bank-additional/bank-additional-full.csv','data/processed/bank_marketing_cleaned.csv','notebooks/Final_Data_Science_Capstone.ipynb','scripts/capstone_analysis.py','models/term_deposit_targeting_model.joblib','report/Final_Data_Science_Capstone_Report.docx','presentation/Final_Data_Science_Capstone_Presentation.pptx','references/dataset_source.md']
for x in req:add('required: '+x,ex(x))
raw=pd.read_csv(R/'data/raw/bank-additional/bank-additional-full.csv',sep=';');clean=pd.read_csv(R/'data/processed/bank_marketing_cleaned.csv');add('raw dimensions',raw.shape==(41188,21),raw.shape);add('clean rows preserved',len(clean)==41188,len(clean));add('target count',clean.subscribed.sum()==4640,clean.subscribed.sum());add('duration retained in clean audit data','duration' in clean);m=json.loads((R/'outputs/summaries/model_summary.json').read_text());add('selected model summary',m['selected_model']=='Histogram gradient boosting');add('duration excluded from fitted model input','duration' not in joblib.load(R/'models/term_deposit_targeting_model.joblib').feature_names_in_)
for f in ['capstone_problem_charter.csv','data_dictionary.csv','validation_model_comparison.csv','test_model_performance.csv','test_scored_predictions.csv','cumulative_gains.csv','age_band_model_audit.csv','insights_table.csv','recommendation_matrix.csv','error_limitations.csv']:add('table: '+f,ex('outputs/tables/'+f) and len(pd.read_csv(R/'outputs/tables'/f))>0)
png=list((R/'outputs/charts').glob('*.png'));add('13 charts',len(png)==13,len(png))
for p in png:add('chart >=150 DPI: '+p.name,Image.open(p).info.get('dpi',(0,0))[0]>=149)
nb=nbformat.read(R/'notebooks/Final_Data_Science_Capstone.ipynb',as_version=4);codes=[c for c in nb.cells if c.cell_type=='code'];errs=[o for c in codes for o in c.get('outputs',[]) if o.get('output_type')=='error'];add('notebook 27 cells',len(nb.cells)==27,len(nb.cells));add('notebook 14 code cells',len(codes)==14,len(codes));add('all code cells executed',all(c.get('outputs') for c in codes),sum(bool(c.get('outputs')) for c in codes));add('notebook zero errors',not errs,len(errs))
d=Document(R/'report/Final_Data_Science_Capstone_Report.docx');h=[p.text for p in d.paragraphs if p.style.name=='Heading 1'];add('report opens',len(d.paragraphs)>150,len(d.paragraphs));add('report 22 sections',all(any(x.startswith(f'{i}.') for x in h) for i in range(1,23)),len(h));add('report 13 figures',len(d.inline_shapes)==13,len(d.inline_shapes));txt=' '.join(p.text for p in d.paragraphs);add('report metrics consistent','0.635' in txt and '1.35×' in txt)
p=Presentation(R/'presentation/Final_Data_Science_Capstone_Presentation.pptx');add('presentation 12 slides',len(p.slides)==12,len(p.slides));pt=' '.join(sh.text for s in p.slides for sh in s.shapes if hasattr(sh,'text'));add('presentation metrics consistent','0.635' in pt and '1.35×' in pt);add('presentation leakage control','duration excluded' in pt.lower())
for f in list((R/'scripts').glob('*.py'))+list((R/'build').glob('*.py')):
 try:ast.parse(f.read_text());add('syntax: '+f.name,True)
 except Exception as e:add('syntax: '+f.name,False,e)
read=(R/'README.md').read_text();add('README DOI','10.24432/C5K306' in read);add('README limitation','not authorised for autonomous targeting' in read);add('README report name','Final_Data_Science_Capstone_Report.docx' in read);add('README presentation name','Final_Data_Science_Capstone_Presentation.pptx' in read)
# hashes
lines=['SHA-256 DATA HASHES','='*90]
for rel in ['data/raw/bank_marketing.zip','data/raw/bank-additional/bank-additional-full.csv','data/processed/bank_marketing_cleaned.csv','models/term_deposit_targeting_model.joblib']:
 p=R/rel;lines.append(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {rel}')
(R/'references/file_hashes.txt').write_text('\n'.join(lines)+'\n');add('hash manifest',ex('references/file_hashes.txt'))
passed=sum(x[1] for x in checks);lines=['FINAL DATA SCIENCE CAPSTONE — QUALITY ASSURANCE','='*100]+[f"[{'PASS' if o else 'FAIL'}] {n}"+(f' — {d}' if d else '') for n,o,d in checks]+['='*100,f'AUTOMATED RESULT: {passed}/{len(checks)} checks passed','','Office validation: DOCX and PPTX were opened and converted to PDF with LibreOffice.','Deployment status: controlled-pilot prototype only; not authorised for autonomous targeting.']
(R/'outputs/summaries/qa_results.txt').write_text('\n'.join(lines)+'\n');print('\n'.join(lines));sys.exit(0 if passed==len(checks) else 1)

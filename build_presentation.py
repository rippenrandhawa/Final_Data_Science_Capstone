"""Build 12-slide capstone executive presentation."""
from pathlib import Path
import json
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN,MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
R=Path(__file__).resolve().parents[1];OUT=R/'presentation/Final_Data_Science_Capstone_Presentation.pptx';C=R/'outputs/charts';S=R/'outputs/summaries';m=json.loads((S/'model_summary.json').read_text())
N=RGBColor(23,54,93);B=RGBColor(47,117,181);L=RGBColor(217,234,247);W=RGBColor(255,255,255);G=RGBColor(100,100,100);O=RGBColor(237,125,49);R1=RGBColor(192,0,0);GR=RGBColor(84,130,53)
p=Presentation();p.slide_width=Inches(13.333);p.slide_height=Inches(7.5)
def bg(s,c=W):s.background.fill.solid();s.background.fill.fore_color.rgb=c
def rect(s,x,y,w,h,c,round=False):z=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if round else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));z.fill.solid();z.fill.fore_color.rgb=c;z.line.fill.background();return z
def text(s,t,x,y,w,h,sz=17,c=N,bold=False,a=PP_ALIGN.LEFT):
 z=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=z.text_frame;tf.clear();tf.word_wrap=True;tf.vertical_anchor=MSO_ANCHOR.MIDDLE;q=tf.paragraphs[0];q.text=t;q.alignment=a
 for r in q.runs:r.font.name='Aptos';r.font.size=Pt(sz);r.font.bold=bold;r.font.color.rgb=c
 return z
def title(s,t,n):rect(s,0,0,13.333,.15,N);text(s,t,.55,.28,11.7,.55,24,N,True);text(s,f'{n:02}',12.25,.3,.55,.4,11,B,True,PP_ALIGN.RIGHT)
def foot(s):text(s,'Final Data Science Capstone  |  UCI Bank Marketing',.55,7.1,8,.22,8,G);text(s,'Pre-call model • duration excluded',10.1,7.1,2.65,.22,8,G,False,PP_ALIGN.RIGHT)
def bullets(s,a,x,y,w,h,sz=16,c=N):
 z=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=z.text_frame;tf.clear();tf.word_wrap=True
 for i,v in enumerate(a):q=tf.paragraphs[0] if i==0 else tf.add_paragraph();q.text='•  '+v;q.font.name='Aptos';q.font.size=Pt(sz);q.font.color.rgb=c;q.space_after=Pt(9)
def img(s,f,x,y,w,h=None):s.shapes.add_picture(str(C/f),Inches(x),Inches(y),width=Inches(w),height=Inches(h) if h else None)
def kpi(s,l,v,x,y,w,c=B):rect(s,x,y,w,1.15,L,True);text(s,v,x+.1,y+.12,w-.2,.48,22,c,True,PP_ALIGN.CENTER);text(s,l,x+.1,y+.68,w-.2,.3,10,N,False,PP_ALIGN.CENTER)
#1
s=p.slides.add_slide(p.slide_layouts[6]);bg(s,N);text(s,'FINAL DATA SCIENCE\nCAPSTONE PROJECT',.75,1.0,7.8,1.6,34,W,True);text(s,'Leakage-Aware Term-Deposit Campaign Targeting',.8,2.8,8,.55,19,RGBColor(180,215,240));rect(s,9.0,.8,.1,5.5,O);text(s,'Business objective',9.5,1.2,2.8,.4,17,W,True);text(s,'Rank likely subscribers before an outbound call—without using post-call information.',9.5,2.0,2.7,1.7,19,W);text(s,'Prepared by: [Your Name]\nData Science Internship',.8,5.8,5,.65,12,W)
#2
s=p.slides.add_slide(p.slide_layouts[6]);bg(s);title(s,'Problem, requirements and success criteria',2);bullets(s,['Outbound calls are costly and customer attention is limited','Prediction point: immediately before the call','Goal: improve subscriber capture per contact','Evaluate with chronological holdout, PR-AUC and lift','Output: ranked decision support—not automatic exclusion'],.7,1.15,6.0,4.9,18);rect(s,7.2,1.25,5.3,4.7,L,True);text(s,'Success means',7.55,1.55,4.5,.4,19,N,True);bullets(s,['Beat prevalence baseline','Exclude call duration leakage','Quantify false positives / negatives','Expose drift and subgroup variation','Define a controlled pilot'],7.55,2.15,4.3,3.1,16);foot(s)
#3
s=p.slides.add_slide(p.slide_layouts[6]);bg(s);title(s,'Real dataset and preparation',3);kpi(s,'Campaign records','41,188',.7,1.15,2.6);kpi(s,'Input variables','20',3.55,1.15,2.25);kpi(s,'Overall subscribers','11.27%',6.05,1.15,2.55);kpi(s,'Period','2008–2010',8.85,1.15,2.7);bullets(s,['UCI Bank Marketing — DOI 10.24432/C5K306, CC BY 4.0','Portuguese bank phone campaigns; full file ordered by date','0 physical null cells; 12,718 semantic “unknown” values retained','Engineered prior-contact, contact-pressure and data-quality features','Original data preserved; cleaned data and dictionary delivered'],.8,3.05,11.3,3.1,16);foot(s)
#4
s=p.slides.add_slide(p.slide_layouts[6]);bg(s);title(s,'Exploration: imbalance and campaign patterns',4);img(s,'01_target_balance.png',.4,1.05,4.0);img(s,'04_previous_outcome.png',4.6,1.1,4.0);img(s,'05_contact_pressure.png',8.7,1.05,4.1);text(s,'Imbalance makes accuracy misleading',.55,5.55,3.7,.55,14,N,True,PP_ALIGN.CENTER);text(s,'Prior success is strongly associated',4.75,5.55,3.7,.55,14,N,True,PP_ALIGN.CENTER);text(s,'More contacts correlate with lower conversion',8.85,5.55,3.6,.55,14,N,True,PP_ALIGN.CENTER);foot(s)
#5
s=p.slides.add_slide(p.slide_layouts[6]);bg(s);title(s,'Leakage control and temporal evaluation',5);img(s,'12_leakage_demo.png',.55,1.05,5.7);rect(s,6.65,1.1,5.95,4.9,L,True);text(s,'Critical design decisions',7.0,1.4,5.2,.4,19,N,True);bullets(s,['Duration is known only after the call → excluded','First 70% train, next 15% validation, last 15% test','No random shuffle of date-ordered records','Model and threshold selected before touching test','Leaky duration model shown only as a warning'],7.0,2.0,5.1,3.2,16);foot(s)
#6
s=p.slides.add_slide(p.slide_layouts[6]);bg(s);title(s,'Model selection and temporal drift',6);img(s,'06_model_comparison.png',.45,1.05,6.3);rect(s,7.05,1.1,5.45,4.9,L,True);text(s,'Prevalence shift',7.4,1.4,4.7,.4,20,R1,True);kpi(s,'Train','5.57%',7.4,2.05,1.4,R1);kpi(s,'Validation','10.65%',9.0,2.05,1.55,O);kpi(s,'Test','38.45%',10.75,2.05,1.4,B);text(s,'Selected: histogram gradient boosting',7.4,3.55,4.7,.4,17,N,True);text(s,'Drift makes absolute probabilities and fixed thresholds unstable. Monitoring and recalibration are mandatory.',7.4,4.15,4.55,1.1,16,N);foot(s)
#7
s=p.slides.add_slide(p.slide_layouts[6]);bg(s);title(s,'Held-out model performance',7);kpi(s,'ROC-AUC',f"{m['test_roc_auc']:.3f}",.7,1.1,2.2);kpi(s,'PR-AUC',f"{m['test_pr_auc']:.3f}",3.15,1.1,2.2);kpi(s,'Precision',f"{m['test_tuned_precision']:.3f}",5.6,1.1,2.2);kpi(s,'Recall',f"{m['test_tuned_recall']:.3f}",8.05,1.1,2.2);kpi(s,'F1',f"{m['test_tuned_f1']:.3f}",10.5,1.1,2.0);img(s,'07_roc_pr_curves.png',.55,2.65,6.3);img(s,'08_confusion_matrix.png',7.3,2.45,4.7);foot(s)
#8
s=p.slides.add_slide(p.slide_layouts[6]);bg(s);title(s,'Business value: ranking lift under limited capacity',8);img(s,'09_cumulative_gains.png',.5,1.0,6.4);rect(s,7.25,1.15,5.1,4.8,L,True);kpi(s,'Top 20% lift',f"{m['top20_lift']:.2f}×",7.65,1.65,2.0,GR);kpi(s,'Contacts','1,235',9.9,1.65,1.9,B);kpi(s,'Subscribers found','639',7.65,3.15,2.0,GR);kpi(s,'Capture rate','26.89%',9.9,3.15,1.9,O);text(s,'Use ranking for a controlled pilot; do not interpret score as guaranteed response.',7.65,4.75,4.1,.75,15,N,True,PP_ALIGN.CENTER);foot(s)
#9
s=p.slides.add_slide(p.slide_layouts[6]);bg(s);title(s,'Interpretability and errors',9);img(s,'10_feature_importance.png',.35,1.0,6.2);img(s,'11_probability_errors.png',6.75,1.0,6.0);text(s,'Importance is predictive—not causal.',.7,6.2,5.3,.4,14,N,True,PP_ALIGN.CENTER);text(s,'Substantial overlap explains FP/FN errors.',7.1,6.2,5.1,.4,14,N,True,PP_ALIGN.CENTER);foot(s)
#10
s=p.slides.add_slide(p.slide_layouts[6]);bg(s);title(s,'Responsible AI and limitations',10);img(s,'13_age_band_audit.png',.4,1.0,6.1);rect(s,6.9,1.05,5.6,5.3,L,True);bullets(s,['Age-band selection and error rates vary','Age use may be legally or ethically restricted','No client ID: repeated clients may cross splits','Historic Portuguese data limits transferability','Observational relationships are not causal','Human override, consent and complaint monitoring required'],7.25,1.45,4.85,4.3,16);foot(s)
#11
s=p.slides.add_slide(p.slide_layouts[6]);bg(s);title(s,'Recommendations and implementation roadmap',11);rows=[('0–30 DAYS','Feature contract, legal/consent review, business economics',R1),('31–60 DAYS','Shadow scoring, calibration and subgroup monitoring',O),('61–90 DAYS','Controlled model-ranked vs random pilot',B),('3–6 MONTHS','Retrain on current data; add offer/cost/client features',GR),('ONGOING','Drift, fairness, complaints and override governance',N)]
for i,(a,b,c) in enumerate(rows):y=1.0+i*1.05;rect(s,.7,y,2.0,.7,c,True);text(s,a,.82,y+.15,1.75,.35,11,W,True,PP_ALIGN.CENTER);text(s,b,3.0,y,9.2,.7,16,N,True);foot(s)
#12
s=p.slides.add_slide(p.slide_layouts[6]);bg(s,N);text(s,'CONCLUSION',.8,.75,3,.4,17,RGBColor(180,215,240),True);text(s,'A useful prototype—\nnot a deployment claim.',.8,1.45,7.7,1.35,31,W,True);bullets(s,[f"Held-out ROC-AUC {m['test_roc_auc']:.3f}; top-20% lift {m['top20_lift']:.2f}×",'Strong temporal drift is the dominant model risk','Duration leakage was identified and prevented','Next step: current-data controlled pilot with governance'],.9,3.25,7.4,2.4,18,W);rect(s,9.3,1.1,.1,5,O);text(s,'Management decision',9.8,1.5,2.5,.4,17,W,True);text(s,'Approve a limited shadow-scoring and pilot phase only after feature, legal, consent and economic review.',9.8,2.25,2.4,2.3,18,W);text(s,'Evidence before automation.',9.8,5.45,2.5,.45,15,RGBColor(180,215,240),True)
p.core_properties.title='Final Data Science Capstone Presentation';p.core_properties.author='[Your Name]';p.core_properties.subject='Leakage-Aware Term-Deposit Campaign Targeting';OUT.parent.mkdir(parents=True,exist_ok=True);p.save(OUT);print('written',OUT,'slides',len(p.slides))

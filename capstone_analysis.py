"""Final Data Science Capstone: leakage-aware bank campaign targeting.

Data: UCI Bank Marketing, bank-additional-full.csv, 41,188 chronological rows,
May 2008–November 2010. DOI: 10.24432/C5K306.

Prediction point: before the outbound call. `duration` is deliberately excluded
because it is only known after a call ends. A duration-inclusive model is trained only
as a leakage demonstration and is never recommended for deployment.
"""
from __future__ import annotations
import json, os, warnings
from pathlib import Path
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss,
 classification_report, confusion_matrix, f1_score, precision_recall_curve,
 precision_score, recall_score, roc_auc_score, roc_curve)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw/bank-additional/bank-additional-full.csv'; CLEAN=ROOT/'data/processed/bank_marketing_cleaned.csv'; CH=ROOT/'outputs/charts'; T=ROOT/'outputs/tables'; S=ROOT/'outputs/summaries'; M=ROOT/'models'
for p in [CLEAN.parent,CH,T,S,M]:p.mkdir(parents=True,exist_ok=True)
sns.set_theme(style='whitegrid'); plt.rcParams.update({'savefig.dpi':200,'figure.dpi':120,'axes.titleweight':'bold','font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})
COL=['#17365D','#2F75B5','#5B9BD5','#70AD47','#ED7D31','#A5A5A5','#C00000']
def save(fig,name):fig.tight_layout();fig.savefig(CH/name,bbox_inches='tight',facecolor='white');plt.close(fig)
def clean():
 raw=pd.read_csv(RAW,sep=';')
 df=raw.copy(); df.columns=df.columns.str.strip().str.lower().str.replace('.','_',regex=False)
 df['subscribed']=(df.pop('y')=='yes').astype(int)
 df['age_band']=pd.cut(df.age,[0,29,39,49,59,69,120],labels=['<30','30–39','40–49','50–59','60–69','70+'])
 df['previously_contacted']=(df.pdays!=999).astype(int)
 df['days_since_previous']=df.pdays.replace(999,np.nan)
 df['contact_pressure']=df.campaign+df.previous
 df['has_credit_obligation']=((df.housing=='yes')|(df.loan=='yes')).astype(int)
 df['unknown_field_count']=(df.select_dtypes('object')=='unknown').sum(axis=1)
 df['source_row']=np.arange(len(df))
 df.to_csv(CLEAN,index=False)
 quality={'rows':len(raw),'raw_columns':len(raw.columns),'clean_columns':len(df.columns),'exact_duplicates':int(raw.duplicated().sum()),'missing_cells_raw':int(raw.isna().sum().sum()),'unknown_category_cells':int((raw.select_dtypes('object')=='unknown').sum().sum()),'target_positive':int(df.subscribed.sum()),'target_rate_pct':float(df.subscribed.mean()*100),'age_min':int(df.age.min()),'age_max':int(df.age.max()),'duration_median_seconds':float(df.duration.median()),'ordered_by_date':True,'period':'May 2008–November 2010 (UCI documentation)'}
 (S/'data_quality.json').write_text(json.dumps(quality,indent=2)); return df,quality

def split(df):
 n=len(df); a=int(n*.70); b=int(n*.85)
 train=df.iloc[:a].copy(); val=df.iloc[a:b].copy(); test=df.iloc[b:].copy()
 rows=[]
 for name,x in [('Train',train),('Validation',val),('Test',test)]:rows.append({'split':name,'start_row':int(x.source_row.min()),'end_row':int(x.source_row.max()),'rows':len(x),'positives':int(x.subscribed.sum()),'positive_rate_pct':x.subscribed.mean()*100})
 pd.DataFrame(rows).to_csv(T/'split_summary.csv',index=False); return train,val,test

def features(df,include_duration=False):
 drop=['subscribed','source_row','age_band']
 if not include_duration:drop.append('duration')
 X=df.drop(columns=drop); y=df.subscribed
 return X,y

def onehot_pipeline(model,X):
 cat=X.select_dtypes(include=['object','string','category']).columns.tolist(); num=[c for c in X.columns if c not in cat]
 pre=ColumnTransformer([('num',Pipeline([('imp',SimpleImputer(strategy='median')),('scale',StandardScaler())]),num),('cat',OneHotEncoder(handle_unknown='ignore',min_frequency=5),cat)])
 return Pipeline([('pre',pre),('model',model)]),num,cat

def ordinal_hgb(X):
 cat=X.select_dtypes(include=['object','string','category']).columns.tolist(); num=[c for c in X.columns if c not in cat]
 pre=ColumnTransformer([('num',SimpleImputer(strategy='median'),num),('cat',Pipeline([('imp',SimpleImputer(strategy='most_frequent')),('ord',OrdinalEncoder(handle_unknown='use_encoded_value',unknown_value=-1))]),cat)])
 mask=[False]*len(num)+[True]*len(cat)
 model=HistGradientBoostingClassifier(max_iter=250,learning_rate=.06,max_leaf_nodes=20,l2_regularization=1.0,categorical_features=mask,random_state=42)
 return Pipeline([('pre',pre),('model',model)]),num,cat

def metric_row(name,y,p,threshold=.5):
 pred=(p>=threshold).astype(int); cm=confusion_matrix(y,pred)
 return {'model':name,'threshold':threshold,'roc_auc':roc_auc_score(y,p),'pr_auc':average_precision_score(y,p),'accuracy':accuracy_score(y,pred),'precision':precision_score(y,pred,zero_division=0),'recall':recall_score(y,pred,zero_division=0),'f1':f1_score(y,pred,zero_division=0),'brier':brier_score_loss(y,p),'tn':int(cm[0,0]),'fp':int(cm[0,1]),'fn':int(cm[1,0]),'tp':int(cm[1,1])}
def lift_at(y,p,fraction):
 n=max(1,int(len(y)*fraction)); idx=np.argsort(-p)[:n]; return float(np.asarray(y)[idx].mean()/np.asarray(y).mean()),int(np.asarray(y)[idx].sum()),n

def model():
 df,q=clean(); train,val,test=split(df); Xtr,ytr=features(train); Xv,yv=features(val); Xt,yt=features(test)
 candidates={}
 log,_,_=onehot_pipeline(LogisticRegression(max_iter=2000,class_weight='balanced',random_state=42),Xtr); candidates['Logistic regression']=log
 rf,_,_=onehot_pipeline(RandomForestClassifier(n_estimators=350,min_samples_leaf=8,max_features='sqrt',class_weight='balanced_subsample',n_jobs=-1,random_state=42),Xtr); candidates['Random forest']=rf
 hgb,_,_=ordinal_hgb(Xtr); candidates['Histogram gradient boosting']=hgb
 val_rows=[]; fitted={}
 for name,pipe in candidates.items():
  pipe.fit(Xtr,ytr); p=pipe.predict_proba(Xv)[:,1]; row=metric_row(name,yv,p,.5); lift,pos,n=lift_at(yv,p,.2);row.update({'top20_lift':lift,'top20_positives':pos,'top20_contacts':n});val_rows.append(row);fitted[name]=pipe
 val_df=pd.DataFrame(val_rows).sort_values('pr_auc',ascending=False);val_df.to_csv(T/'validation_model_comparison.csv',index=False)
 selected=val_df.iloc[0].model; pval=fitted[selected].predict_proba(Xv)[:,1]; precision,recall,thresholds=precision_recall_curve(yv,pval);f1=2*precision*recall/(precision+recall+1e-12);best_i=np.nanargmax(f1[:-1]);threshold=float(thresholds[best_i])
 # refit on all pre-test data
 pretest=pd.concat([train,val]); Xpre,ypre=features(pretest); final=candidates[selected]; final.fit(Xpre,ypre); ptest=final.predict_proba(Xt)[:,1]
 test_rows=[]
 base=np.full(len(yt),ypre.mean());test_rows.append(metric_row('Prevalence baseline',yt,base,.5))
 row=metric_row(selected,yt,ptest,.5); row['decision_rule']='default 0.50';test_rows.append(row)
 row=metric_row(selected+' (validation-tuned threshold)',yt,ptest,threshold); row['decision_rule']='max validation F1';test_rows.append(row)
 for r in test_rows:
  lift,pos,n=lift_at(yt,ptest if 'Prevalence' not in r['model'] else base,.2);r.update({'top20_lift':lift,'top20_positives':pos,'top20_contacts':n})
 test_df=pd.DataFrame(test_rows);test_df.to_csv(T/'test_model_performance.csv',index=False)
 # Leakage demo using logistic + duration
 Xpt_l,ypt_l=features(pretest,True); Xt_l,yt_l=features(test,True); leak,_,_=onehot_pipeline(LogisticRegression(max_iter=2000,class_weight='balanced',random_state=42),Xpt_l); leak.fit(Xpt_l,ypt_l); pleak=leak.predict_proba(Xt_l)[:,1]
 leak_df=pd.DataFrame([{'model':'Deployable model (duration excluded)','roc_auc':roc_auc_score(yt,ptest),'pr_auc':average_precision_score(yt,ptest)}, {'model':'Diagnostic leakage model (duration included)','roc_auc':roc_auc_score(yt,pleak),'pr_auc':average_precision_score(yt,pleak)}]);leak_df.to_csv(T/'leakage_demonstration.csv',index=False)
 # Scoring output and errors
 scored=test[['source_row','age','age_band','job','month','campaign','previous','poutcome','subscribed']].copy();scored['probability']=ptest;scored['prediction']=(ptest>=threshold).astype(int);scored['error_type']=np.select([(scored.subscribed==0)&(scored.prediction==1),(scored.subscribed==1)&(scored.prediction==0)],['False positive','False negative'],'Correct');scored.to_csv(T/'test_scored_predictions.csv',index=False)
 # gains table
 order=np.argsort(-ptest); yy=np.asarray(yt)[order]; gains=[]
 for dec in range(1,11):
  n=int(np.ceil(len(yy)*dec/10)); captured=yy[:n].sum(); gains.append({'contact_fraction_pct':dec*10,'contacts':n,'subscribers_captured':int(captured),'capture_rate_pct':captured/yy.sum()*100,'lift':(captured/n)/yy.mean()})
 pd.DataFrame(gains).to_csv(T/'cumulative_gains.csv',index=False)
 # subgroup metrics threshold tuned
 sub=[]
 for band,g in scored.groupby('age_band',observed=True):
  if len(g)<20:continue
  sub.append({'age_band':band,'rows':len(g),'positive_rate_pct':g.subscribed.mean()*100,'selection_rate_pct':g.prediction.mean()*100,'precision':precision_score(g.subscribed,g.prediction,zero_division=0),'recall':recall_score(g.subscribed,g.prediction,zero_division=0),'false_positive_rate':((g.subscribed==0)&(g.prediction==1)).sum()/max(1,(g.subscribed==0).sum())})
 pd.DataFrame(sub).to_csv(T/'age_band_model_audit.csv',index=False)
 # permutation importance original features
 sample_idx=np.linspace(0,len(Xt)-1,min(2500,len(Xt))).astype(int); pi=permutation_importance(final,Xt.iloc[sample_idx],yt.iloc[sample_idx],scoring='average_precision',n_repeats=5,random_state=42,n_jobs=-1);imp=pd.DataFrame({'feature':Xt.columns,'importance_mean':pi.importances_mean,'importance_std':pi.importances_std}).sort_values('importance_mean',ascending=False);imp.to_csv(T/'permutation_importance.csv',index=False)
 joblib.dump(final,M/'term_deposit_targeting_model.joblib')
 summary={'selected_model':selected,'threshold':threshold,'raw_rows':len(df),'overall_positive_rate_pct':df.subscribed.mean()*100,'train_rows':len(train),'validation_rows':len(val),'test_rows':len(test),'test_positive_rate_pct':yt.mean()*100,'test_roc_auc':roc_auc_score(yt,ptest),'test_pr_auc':average_precision_score(yt,ptest),'test_default_f1':f1_score(yt,ptest>=.5),'test_tuned_precision':precision_score(yt,ptest>=threshold,zero_division=0),'test_tuned_recall':recall_score(yt,ptest>=threshold,zero_division=0),'test_tuned_f1':f1_score(yt,ptest>=threshold,zero_division=0),'test_brier':brier_score_loss(yt,ptest),'top20_lift':lift_at(yt,ptest,.2)[0],'top20_subscribers':lift_at(yt,ptest,.2)[1],'top20_contacts':lift_at(yt,ptest,.2)[2],'test_subscribers':int(yt.sum()),'leakage_roc_auc':roc_auc_score(yt,pleak),'leakage_pr_auc':average_precision_score(yt,pleak)}
 (S/'model_summary.json').write_text(json.dumps(summary,indent=2)); make_tables(df,scored); charts(df,val_df,test_df,ptest,yt,threshold,imp,scored,leak_df); print(json.dumps(summary,indent=2)); return summary

def make_tables(df,scored):
 conv=[]
 for c in ['job','month','contact','poutcome','education','housing','loan']:
  x=df.groupby(c).subscribed.agg(['count','sum','mean']).reset_index();x.columns=[c,'campaign_records','subscriptions','conversion_rate'];x['feature']=c;x=x.rename(columns={c:'segment'});conv.append(x[['feature','segment','campaign_records','subscriptions','conversion_rate']])
 pd.concat(conv).to_csv(T/'segment_conversion_rates.csv',index=False)
 desc=df[['age','campaign','previous','days_since_previous','duration','subscribed']].describe().T;desc.to_csv(T/'descriptive_statistics.csv')

def charts(df,val_df,test_df,p,y,thr,imp,scored,leak):
 #1 target
 x=df.subscribed.value_counts().sort_index();fig,ax=plt.subplots(figsize=(6,4));bars=ax.bar(['No subscription','Subscribed'],x,color=[COL[5],COL[3]]);ax.bar_label(bars,labels=[f'{v:,}\n({v/len(df):.1%})' for v in x]);ax.set(title='Term-Deposit Subscription Outcome',ylabel='Campaign records');save(fig,'01_target_balance.png')
 #2 month conversion
 x=df.groupby('month').subscribed.agg(['count','mean']).reindex(['mar','apr','may','jun','jul','aug','sep','oct','nov','dec']);fig,ax=plt.subplots(figsize=(8,4.5));ax.bar(x.index,x['mean']*100,color=COL[1]);ax.set(title='Subscription Rate by Contact Month',xlabel='Month',ylabel='Subscription rate (%)');save(fig,'02_month_conversion.png')
 #3 job
 x=df.groupby('job').subscribed.mean().sort_values();fig,ax=plt.subplots(figsize=(8,5));ax.barh(x.index,x*100,color=COL[2]);ax.set(title='Subscription Rate by Job Category',xlabel='Subscription rate (%)',ylabel='');save(fig,'03_job_conversion.png')
 #4 previous outcome
 x=df.groupby('poutcome').subscribed.mean().sort_values();fig,ax=plt.subplots(figsize=(7,4));bars=ax.bar(x.index,x*100,color=COL[3]);ax.bar_label(bars,fmt='%.1f%%');ax.set(title='Subscription Rate by Previous Campaign Outcome',xlabel='Previous outcome',ylabel='Subscription rate (%)');save(fig,'04_previous_outcome.png')
 #5 campaign contacts
 cap=df.campaign.clip(upper=10);x=df.assign(campaign_capped=cap).groupby('campaign_capped').subscribed.agg(['count','mean']);fig,ax=plt.subplots(figsize=(8,4.5));ax.plot(x.index,x['mean']*100,marker='o',color=COL[0]);ax.set(title='Conversion Rate vs Current-Campaign Contact Count',xlabel='Contacts (10 = 10 or more)',ylabel='Subscription rate (%)');save(fig,'05_contact_pressure.png')
 #6 validation compare
 x=val_df.sort_values('pr_auc');fig,ax=plt.subplots(figsize=(8,4.5));ax.barh(x.model,x.pr_auc,color=COL[1]);ax.set(title='Model Selection on Chronological Validation Set',xlabel='Average precision (PR-AUC)',ylabel='');save(fig,'06_model_comparison.png')
 #7 ROC/PR
 fig,axs=plt.subplots(1,2,figsize=(10,4.3));fpr,tpr,_=roc_curve(y,p);axs[0].plot(fpr,tpr,color=COL[0],label=f'AUC {roc_auc_score(y,p):.3f}');axs[0].plot([0,1],[0,1],'--',color='grey');axs[0].set(title='ROC Curve — Test Set',xlabel='False-positive rate',ylabel='True-positive rate');axs[0].legend();pr,re,_=precision_recall_curve(y,p);axs[1].plot(re,pr,color=COL[4],label=f'AP {average_precision_score(y,p):.3f}');axs[1].axhline(np.mean(y),ls='--',color='grey',label=f'Baseline {np.mean(y):.3f}');axs[1].set(title='Precision–Recall Curve — Test Set',xlabel='Recall',ylabel='Precision');axs[1].legend();save(fig,'07_roc_pr_curves.png')
 #8 confusion
 cm=confusion_matrix(y,p>=thr);fig,ax=plt.subplots(figsize=(5.5,4.5));sns.heatmap(cm,annot=True,fmt=',',cmap='Blues',cbar=False,ax=ax);ax.set(title=f'Confusion Matrix at Validation-Tuned Threshold ({thr:.3f})',xlabel='Predicted',ylabel='Actual');ax.set_xticklabels(['No','Yes']);ax.set_yticklabels(['No','Yes'],rotation=0);save(fig,'08_confusion_matrix.png')
 #9 gains
 yy=np.asarray(y)[np.argsort(-p)];fra=[];cap=[]
 for i in range(1,101):n=max(1,int(len(yy)*i/100));fra.append(i);cap.append(yy[:n].sum()/yy.sum()*100)
 fig,ax=plt.subplots(figsize=(7,4.5));ax.plot(fra,cap,color=COL[0],label='Model');ax.plot([0,100],[0,100],'--',color='grey',label='Random');ax.axvline(20,color=COL[4],ls=':');ax.set(title='Cumulative Gains — Test Set',xlabel='Clients contacted (%)',ylabel='Subscribers captured (%)');ax.legend();save(fig,'09_cumulative_gains.png')
 #10 importance
 x=imp.head(12).sort_values('importance_mean');fig,ax=plt.subplots(figsize=(8,5));ax.barh(x.feature,x.importance_mean,color=COL[2]);ax.set(title='Permutation Importance on Held-Out Test Sample',xlabel='Decrease in average precision',ylabel='Feature');save(fig,'10_feature_importance.png')
 #11 error prob
 fig,ax=plt.subplots(figsize=(8,4.5));sns.histplot(data=scored,x='probability',hue='subscribed',bins=35,stat='density',common_norm=False,element='step',palette=[COL[5],COL[3]],ax=ax);ax.axvline(thr,color=COL[6],ls='--',label='Threshold');ax.set(title='Predicted Probability by Actual Outcome',xlabel='Predicted subscription probability',ylabel='Density');save(fig,'11_probability_errors.png')
 #12 leakage
 fig,ax=plt.subplots(figsize=(7,4));x=leak.set_index('model').roc_auc.sort_values();bars=ax.barh(['Deployable\n(no duration)','Leaky diagnostic\n(with duration)'],x.values,color=[COL[1],COL[6]]);ax.bar_label(bars,fmt='%.3f');ax.set(title='Why Call Duration Must Be Excluded',xlabel='Test ROC-AUC',xlim=(.5,1));save(fig,'12_leakage_demo.png')
 #13 age audit
 audit=pd.read_csv(T/'age_band_model_audit.csv');fig,ax=plt.subplots(figsize=(8,4.5));w=.35;xx=np.arange(len(audit));ax.bar(xx-w/2,audit.recall,w,label='Recall',color=COL[1]);ax.bar(xx+w/2,audit.precision,w,label='Precision',color=COL[4]);ax.set_xticks(xx,audit.age_band);ax.set(title='Model Performance Audit by Age Band',xlabel='Age band',ylabel='Metric');ax.legend();save(fig,'13_age_band_audit.png')
if __name__=='__main__':model()

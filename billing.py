"""Monthly billing: call-level minute rounding and monthly GB rounding."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind

PLAN_COLS=['usd_monthly_pay','minutes_included','messages_included','mb_per_month_included','usd_per_minute','usd_per_message','usd_per_gb']

def _require(frame,cols,label):
    missing=set(cols)-set(frame.columns)
    if missing: raise ValueError(f'{label}: missing columns {sorted(missing)}')

def invoice_months(users,plans,calls,messages,internet,start='2018-01-01',end='2018-12-31'):
    """Charge full monthly fee for every subscribed month, including zero usage.

    Registration and churn months are included without proration, an explicit
    educational-case assumption. A user's plan is assumed constant in this table.
    start/end must bound complete months; no claims of realized company revenue.
    """
    _require(users,['user_id','plan','reg_date','churn_date'],'users')
    _require(plans,['plan_name']+PLAN_COLS,'plans')
    _require(calls,['id','user_id','call_date','duration'],'calls')
    _require(messages,['id','user_id','message_date'],'messages')
    _require(internet,['id','user_id','session_date','mb_used'],'internet')
    users,plans=users.copy(),plans.copy()
    for frame,key in [(users,'user_id'),(plans,'plan_name')]:
        if frame[key].isna().any() or frame[key].duplicated().any(): raise ValueError(f'Invalid {key}')
    if not users['plan'].isin(plans['plan_name']).all(): raise ValueError('Unknown plan')
    vals=plans[PLAN_COLS].apply(pd.to_numeric,errors='raise')
    if not np.isfinite(vals).all().all() or (vals<0).any().any(): raise ValueError('Invalid plan rates')
    plans[PLAN_COLS]=vals
    if not (plans['mb_per_month_included']%1024==0).all(): raise ValueError('This case requires whole-GB allowances')
    start,end=pd.Timestamp(start),pd.Timestamp(end)
    if start.day!=1 or end!=end.to_period('M').end_time.normalize() or end<start:
        raise ValueError('Window must contain complete calendar months')
    users['reg_date']=pd.to_datetime(users['reg_date'],errors='raise')
    users['churn_date']=pd.to_datetime(users['churn_date'],errors='raise')
    if users['reg_date'].isna().any() or (users['churn_date']<users['reg_date']).any(): raise ValueError('Invalid subscription dates')
    records=[]
    for row in users.itertuples(index=False):
        begin=max(row.reg_date,start)
        finish=min(row.churn_date if pd.notna(row.churn_date) else end,end)
        if finish<begin: continue
        for month in pd.period_range(begin,finish,freq='M'):
            records.append({'user_id':row.user_id,'plan':row.plan,'month':str(month)})
    panel=pd.DataFrame(records,columns=['user_id','plan','month'])
    if panel.empty: raise ValueError('No subscriptions in analysis window')
    def aggregate(frame,date,value,output):
        frame=frame.copy()
        if frame['id'].isna().any() or frame['id'].duplicated().any(): raise ValueError('Duplicate or missing event id')
        if not frame['user_id'].isin(users['user_id']).all(): raise ValueError('Unknown event user')
        frame[date]=pd.to_datetime(frame[date],errors='raise')
        if frame[date].isna().any(): raise ValueError('Missing event date')
        if value:
            frame[value]=pd.to_numeric(frame[value],errors='raise')
            if not np.isfinite(frame[value]).all() or not frame[value].ge(0).all(): raise ValueError('Invalid usage')
        frame=frame.merge(users[['user_id','reg_date','churn_date']],on='user_id',validate='many_to_one')
        if ((frame[date]<frame['reg_date']) | (frame[date]>frame['churn_date'])).any(): raise ValueError('Usage outside subscription')
        frame=frame.loc[frame[date].between(start,end)].copy()
        frame['month']=frame[date].dt.to_period('M').astype(str)
        if value=='duration': frame[value]=np.ceil(frame[value])
        group=frame.groupby(['user_id','month'])
        series=group[value].sum() if value else group.size()
        if value=='mb_used': series=np.ceil(series/1024)
        return series.rename(output).reset_index()
    for events,date,value,label in [(calls,'call_date','duration','minutes'),(messages,'message_date',None,'messages'),(internet,'session_date','mb_used','gb')]:
        panel=panel.merge(aggregate(events,date,value,label),on=['user_id','month'],how='left',validate='one_to_one')
    panel[['minutes','messages','gb']]=panel[['minutes','messages','gb']].fillna(0)
    panel=panel.merge(plans,left_on='plan',right_on='plan_name',validate='many_to_one')
    panel['extra_minute_usd']=(panel['minutes']-panel['minutes_included']).clip(lower=0)*panel['usd_per_minute']
    panel['extra_message_usd']=(panel['messages']-panel['messages_included']).clip(lower=0)*panel['usd_per_message']
    panel['extra_data_usd']=(panel['gb']-panel['mb_per_month_included']/1024).clip(lower=0)*panel['usd_per_gb']
    panel['revenue_usd']=panel[['usd_monthly_pay','extra_minute_usd','extra_message_usd','extra_data_usd']].sum(axis=1).round(2)
    return panel[['user_id','plan','month','minutes','messages','gb','usd_monthly_pay','extra_minute_usd','extra_message_usd','extra_data_usd','revenue_usd']]

def compare_plans(invoices,first='surf',second='ultimate'):
    """Welch comparison using one average monthly invoice per user.

    Equal user weighting avoids pretending repeated user-months are independent.
    Observational allocation still prevents causal interpretation.
    """
    if invoices.groupby('user_id')['plan'].nunique().gt(1).any(): raise ValueError('A user spans multiple plans')
    per_user=invoices.groupby(['user_id','plan'],as_index=False)['revenue_usd'].mean()
    a=per_user.loc[per_user['plan'].eq(first),'revenue_usd']
    b=per_user.loc[per_user['plan'].eq(second),'revenue_usd']
    if len(a)<2 or len(b)<2: raise ValueError('Need at least two users per plan')
    if a.var()+b.var()==0: raise ValueError('No within-group variation')
    test=ttest_ind(a,b,equal_var=False)
    return {'unit':'user mean monthly invoice','first_plan':first,'second_plan':second,
            'users_first':len(a),'users_second':len(b),'mean_first_usd':float(a.mean()),
            'mean_second_usd':float(b.mean()),'difference_usd':float(a.mean()-b.mean()),
            'welch_statistic':float(test.statistic),'p_value':float(test.pvalue)}

def load_invoices(data_dir,**kwargs):
    p=Path(data_dir)
    return invoice_months(*(pd.read_csv(p/f'megaline_{name}.csv') for name in ['users','plans','calls','messages','internet']),**kwargs)

def synthetic_tables():
    users=pd.DataFrame({'user_id':[1,2], 'plan':['demo','demo'], 'reg_date':['2018-01-01']*2, 'churn_date':[None,None]})
    plans=pd.DataFrame([dict(plan_name='demo',usd_monthly_pay=20,minutes_included=1,messages_included=1,mb_per_month_included=1024,usd_per_minute=0.03,usd_per_message=0.03,usd_per_gb=10)])
    calls=pd.DataFrame({'id':['c1','c2'],'user_id':[1,1],'call_date':['2018-01-05']*2,'duration':[0.1,1.1]})
    messages=pd.DataFrame({'id':['m1','m2'],'user_id':[1,1],'message_date':['2018-01-05']*2})
    internet=pd.DataFrame({'id':['i1','i2'],'user_id':[1,1],'session_date':['2018-01-05']*2,'mb_used':[600,425]})
    return users,plans,calls,messages,internet

def demo():
    invoices=invoice_months(*synthetic_tables(),start='2018-01-01',end='2018-01-31')
    return {'dataset':'synthetic fixture','invoices':invoices.to_dict('records')}

if __name__=='__main__': print(json.dumps(demo(),indent=2))

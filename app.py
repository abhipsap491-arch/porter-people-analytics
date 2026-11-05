import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
st.set_page_config(page_title="PORTER | People Analytics — Abhipsa Parida", layout="wide", page_icon="🚚", initial_sidebar_state="expanded")
import plotly.io as pio
import plotly.graph_objects as go
PORTER_BLUE="#0648C8"
PORTER_NAVY="#062C87"
PORTER_SKY="#3B91FF"
PORTER_YELLOW="#FFD541"
PORTER_RED="#E64B5D"
pio.templates.default="plotly_white"
px.defaults.color_discrete_sequence=[PORTER_BLUE,PORTER_SKY,PORTER_YELLOW,"#67B8F5","#0D2B73",PORTER_RED]
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*=css],.stApp{font-family:Inter,Arial,sans-serif!important}
.stApp{background:#F3F7FF;color:#122348}
section[data-testid="stSidebar"]{background:linear-gradient(165deg,#062C87 0%,#0648C8 75%,#0B63E5 100%)}
section[data-testid="stSidebar"] *{color:#FFFFFF!important}
section[data-testid="stSidebar"] div[data-baseweb="select"] *{color:#152B55!important}
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p{color:#DCE9FF!important}
.stApp h1,.stApp h2,.stApp h3{color:#092F86;letter-spacing:-.025em}
.stApp h1{font-weight:800;font-size:2.05rem}
.stApp h3{font-weight:750}
div[data-testid="stMetric"]{background:#fff;padding:20px 19px;border-radius:15px;border:1px solid #DDE8FA;box-shadow:0 3px 15px rgba(6,44,135,.055)}
div[data-testid="stMetricLabel"]{color:#536681}
div[data-testid="stMetricValue"]{color:#073BBD;font-weight:800}
[data-testid="stPlotlyChart"]{background:#fff;border:1px solid #E0E9F9;border-radius:15px;padding:10px;box-shadow:0 3px 12px rgba(6,44,135,.035)}
[data-testid="stDataFrame"]{border:1px solid #DCE7F8;border-radius:12px}
.stButton button,.stDownloadButton button{background:#0648C8;color:white;border-radius:10px;border:0;font-weight:650}
.stSelectbox label,.stMultiSelect label{font-weight:650}
.porter-hero{background:linear-gradient(115deg,#062C87,#0648C8 70%,#1675EF);padding:23px 27px;border-radius:17px;color:white;margin-bottom:20px;box-shadow:0 8px 25px rgba(6,44,135,.13)}
.porter-hero .brand{font-weight:850;font-size:27px;letter-spacing:-1.3px}
.porter-hero .subtitle{font-size:14px;color:#E2EDFF;margin-top:7px}
.porter-pill{display:inline-block;background:#FFD541;color:#072D78;font-size:11px;font-weight:800;padding:5px 11px;border-radius:100px;margin-left:12px;vertical-align:middle}
</style>""",unsafe_allow_html=True)
st.markdown('<div class="porter-hero"><div class="brand">PORTER <span class="porter-pill">PEOPLE ANALYTICS</span></div><div class="subtitle">Employee Experience &amp; Talent Acquisition | Leadership Intelligence | 2026</div></div>',unsafe_allow_html=True)
D=Path(__file__).parent/'data'
@st.cache_data
def load(n):return pd.read_csv(D/f'{n}.csv',low_memory=False)
S=load('survey');C=load('candidates');R=load('requisitions');E=load('employees')
for col in ['Submitted On']:S[col]=pd.to_datetime(S[col],errors='coerce')
for col in ['Applied On','Offer Released On','Actual DOJ','R1 Interview Date','R1 Feedback Submitted On']:C[col]=pd.to_datetime(C[col],errors='coerce')
st.sidebar.markdown('### 🚚 PORTER\n**People Analytics**')
st.caption('Prepared by Abhipsa Parida | ID: 2025H1540816P  •  Synthetic case data  •  Filter-aware KPIs')
page=st.sidebar.radio('Workspace',['Employee experience','Talent acquisition','Data quality & methodology'])
def filters(df,cols):
 for c in cols:
  if c in df:
   opts=sorted(df[c].dropna().astype(str).unique());sel=st.sidebar.multiselect(c,opts,key=f'{page}_{c}')
   if sel:df=df[df[c].astype(str).isin(sel)]
 return df
def enps(df):
 x=pd.to_numeric(df['score'],errors='coerce').dropna();return 100*((x>=9).sum()-(x<=6).sum())/len(x) if len(x) else None
def metric(label,value):st.metric(label,value)
if page=='Employee experience':
 st.header('Employee Experience & eNPS')
 st.caption('Sentiment, engagement drivers, and workforce segment trends')
 st.sidebar.header('Slice employee population');d=filters(S,['wave','Thread','Function','Grade','Location'])
 a,b,c,d4=st.columns(4)
 a.metric('Responses',f'{d.score.notna().sum():,}');b.metric('eNPS',f'{enps(d):+.1f}' if enps(d) is not None else 'N/A');c.metric('Promoters',f'{(d.score>=9).sum():,}');d4.metric('Detractors',f'{(d.score<=6).sum():,}')
 st.subheader('Survey-wave trend')
 trend=d.groupby('wave').apply(lambda x:pd.Series({'eNPS':enps(x),'n':x.score.notna().sum()}),include_groups=False).reset_index()
 st.plotly_chart(px.bar(trend,x='wave',y='eNPS',text='n',title='eNPS by wave (labels show valid n)',color='wave'),use_container_width=True)
 st.subheader('Sentiment drivers')
 keys=['feedback','pay','workload','onboarding','growth'];driver=d.groupby('wave')[keys].mean().reset_index().melt(id_vars='wave',var_name='Dimension',value_name='Mean rating')
 st.plotly_chart(px.bar(driver,x='Dimension',y='Mean rating',color='wave',barmode='group',range_y=[0,5]),use_container_width=True)
 st.subheader('Drill down | segment comparisons')
 group=st.selectbox('Group by',['Function','Thread','Grade','Location'])
 seg=d.groupby(group,dropna=False).apply(lambda x:pd.Series({'n':x.score.notna().sum(),'eNPS':enps(x)}),include_groups=False).reset_index();seg=seg[seg.n>=10].sort_values('eNPS')
 st.plotly_chart(px.bar(seg,x=group,y='eNPS',hover_data=['n'],title='Segments with at least 10 valid responses'),use_container_width=True)
 st.dataframe(seg,use_container_width=True,hide_index=True)
 st.caption('eNPS = 100 × (promoters 9–10 − detractors 0–6) / valid responses. No inference of causality.')
elif page=='Talent acquisition':
 st.header('Recruitment & Hiring Performance')
 st.caption('Candidate funnel, hiring throughput, feedback delays, and source effectiveness')
 st.sidebar.header('Slice recruitment');d=filters(C,['Thread','Function','Grade','Location','Recruiter','Source','Criticality'])
 a,b,c,d4=st.columns(4)
 a.metric('Candidates',f'{d["Candidate ID"].nunique():,}');b.metric('Offers',f'{d["Offer Released On"].notna().sum():,}');c.metric('Joins',f'{d["Actual DOJ"].notna().sum():,}');d4.metric('Median R1 feedback',f'{d.feedback_days.median():.1f} days' if d.feedback_days.notna().any() else 'N/A')
 st.subheader('Funnel events (not mutually exclusive)')
 stages=['Applied On','Shortlisted On','Screening Done On','R1 Interview Date','R2 Interview Date','Offer Released On','Actual DOJ'];counts=[d[c].notna().sum() for c in stages]
 st.plotly_chart(px.funnel(x=counts,y=['Applied','Shortlisted','Screened','R1','R2','Offer','Joined'],title='Recorded candidate milestones'),use_container_width=True)
 left,right=st.columns(2)
 with left:
  st.subheader('Monthly offer releases');monthly=d.dropna(subset=['Offer Released On']).groupby(d['Offer Released On'].dt.to_period('M')).size().reset_index(name='Offers');monthly['Month']=monthly['Offer Released On'].astype(str)
  st.plotly_chart(px.line(monthly,x='Month',y='Offers',markers=True),use_container_width=True)
 with right:
  st.subheader('Source conversion');src=d.groupby('Source',dropna=False).agg(Candidates=('Candidate ID','nunique'),Offers=('Offer Released On','count')).reset_index();src['Offer rate (%)']=100*src.Offers/src.Candidates
  st.plotly_chart(px.bar(src,x='Source',y='Offer rate (%)',hover_data=['Candidates','Offers']),use_container_width=True)
 st.subheader('Drill down | recruiter / function / source')
 group=st.selectbox('Group by',['Recruiter','Function','Source','Grade','Location'])
 g=d.groupby(group,dropna=False).agg(Candidates=('Candidate ID','nunique'),Offers=('Offer Released On','count'),Joins=('Actual DOJ','count'),Median_feedback_days=('feedback_days','median'),Median_join_days=('join_days','median')).reset_index()
 st.dataframe(g.sort_values('Candidates',ascending=False),use_container_width=True,hide_index=True)
 st.caption('Unmatched requisition candidates retained in overall candidate totals; requisition-specific fields are missing for these records. Time-to-join excludes missing/negative intervals.')
else:
 st.header('Data Quality & Methodology')
 st.subheader('Data validation & reproducibility');q=pd.read_csv(Path(__file__).parent/'data_quality_log.csv');st.dataframe(q,use_container_width=True,hide_index=True)
 st.markdown('**Key caveats:** Synthetic observational data; survey response composition may change. Missing event dates are not zeros. Requisition joins are not unique fill counts. No causal claims. Metrics recalculate on the filtered candidate/response cohort.')
 st.markdown('**Cleaning:** Normalized survey-wave labels; deduplicated by ID and timestamp; standardized Excel serial dates and CTC values; excluded invalid eNPS scores; joined employee and requisition dimensions with unmatched records retained and flagged.')
 st.download_button('Download data-quality log',q.to_csv(index=False),file_name='data_quality_log.csv')

st.divider()
st.caption('PORTER | People Analytics case submission • Abhipsa Parida • 2025H1540816P • Synthetic datasets • Calculations are observational, not causal')

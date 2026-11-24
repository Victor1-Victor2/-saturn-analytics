"""SATURN Analytics: demostració pública amb dades 100% sintètiques.
No llegeix fitxers reals, no desa dades i no exposa cap funció de pujada.
"""
import math
from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(page_title='SATURN Analytics · Demo', page_icon='📊', layout='wide', initial_sidebar_state='collapsed')
st.markdown('''<style>
.block-container{max-width:1250px;padding-top:1.5rem;padding-bottom:2rem}
.stApp{background:#f7f9fc}h1,h2,h3{color:#12385b}
.hero{background:#103454;color:white;padding:24px;border-radius:14px;margin-bottom:16px}
.hero h1{color:white;font-size:1.65rem;margin:0}.hero p{color:#d2e3f2;margin:5px 0 0}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:12px 0 20px}
.kpi{background:#e9f2fb;border-radius:12px;padding:15px;min-width:0}
.kpi .lbl{color:#526c83;font-size:.8rem}.kpi .val{color:#12385b;font-size:1.5rem;font-weight:750;overflow-wrap:anywhere}
@media(max-width:850px){.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:420px){.kpis{grid-template-columns:1fr 1fr;gap:8px}.kpi{padding:10px}.kpi .val{font-size:1.15rem}.hero{padding:16px}}
</style>''',unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>SATURN Analytics WEB · V1.2.1</h1><p>Demostració pública · dades fictícies · sense connexió PLC</p></div>',unsafe_allow_html=True)
st.warning('DEMO: totes les xifres, projectes i dates d’aquesta pàgina són inventats. No hi ha dades de clients ni captures reals.')
projects=['P1001','P1002','P1003']
project=st.selectbox('Número de projecte (fictici)',projects)
idx=projects.index(project)
base=24500+idx*10500
kpis=[
 ('1.1 Projecte',project),('1.2 OEE sr',f'{88+idx}%'),('1.3 Availability',f'{91+idx}%'),('1.4 Quality','98%'),('1.5 Cadència',f'{17+idx}'),('1.6 OEE',f'{83+idx}%'),
 ('2.1 Palets totals · DB4000',f'{base:,}'.replace(',','.')),('2.2 Pallets/hour LP',str(75+idx*4)),('2.3 Average P/H',str(61+idx*3)),('2.4 Palets dia',str(175+idx*15)),('2.5 Palets mes',str(3200+idx*230)),('2.6 Prog +1000','0'),
 ('3.1 Voltes totals',f'{base*14:,}'.replace(',','.')),('3.2 Wraps LP','14'),('3.3 Average V/P','14'),('3.4 Height detected','540'),('3.5 Main Prog','1'),('3.6 Palets Main','120'),
 ('4.1 Hores encesa','2840'),('4.2 Hores Auto','2570'),('4.3 Hores treball','1900'),('4.4 Hores alarma','8'),('4.5 Hores No Auto','262'),('4.6 Changes <3','2'),
 ('5.1 Registre','2026-01-15'),('5.2 Sector','No publicat'),('5.3 V/P Reg','14'),('5.4 Tipus','No publicat'),('5.5 Max. T. Value','55'),('5.6 Preestiro','150'),
 ('6.1 Program','1'),('6.2 Single / Double','0'),('6.3 Press plate','0'),('6.4 Cover','0'),('6.5 Wrapping RPM','25'),('6.6 Wrapping tension','50'),
 ('7.1 Pallets 24CB','210'),('7.2 Mitjana 24CB','11'),('7.3 Mitjana canvis','12'),('7.4 3<Changes<45','15'),('7.5 45<Changes<80','1'),('7.6 80>Changes','0'),
 ('8.1 Total emergències','8'),('8.2 Pallets per alarma','3062'),('8.3 Barrera entrada','3'),('8.4 Barrera sortida','2'),('8.5 PLC On/Off','4'),('8.6 Enfardat >180s','0')]
import html
st.subheader('Indicadors de rendiment')
st.caption('48 KPI de demostració · valors sintètics')
parts=[]
for label,val in kpis:
    parts.append(f'<div class="kpi"><div class="lbl">{html.escape(label)}</div><div class="val">{html.escape(val)}</div></div>')
st.markdown('<div class="kpis">'+''.join(parts)+'</div>',unsafe_allow_html=True)

# Dades exclusivament sintètiques per provar el disseny públic.
BLUE='#1874b9'
DARK='#12385b'
LIGHT='#e7eff8'
CHART_CONFIG = dict(displayModeBar=False, scrollZoom=False, doubleClick=False, showTips=False, responsive=True)


hours=[max(0,round(8+7*math.sin((i+idx)*.64)+4*math.sin(i*1.9))) for i in range(24)]
days=[max(0,round(160+50*math.sin(i*.53+idx)+25*math.cos(i*.9))) for i in range(30)]
months=[max(0,round(2900+700*math.sin(i*.8+idx))) for i in range(12)]
rolls=[max(0,round(12+7*math.sin(i*.71+idx))) for i in range(24)]
annual=[max(0,round(base*(i+1)/10)) for i in range(10)]

# Distribució de programes sintètica, diferent per projecte.
programs={'Programa 1': 620+idx*110, 'Programa 3': 265+idx*35,
          'Programa 5': 130+idx*20, 'Programa 0': 58+idx*8,
          'Altres': 42+idx*6}

def fmt(n):
    return f'{n:,.0f}'.replace(',','.')

def bar_chart(title, labels, values, unit='palets', height=300, sparse=1):
    fig=go.Figure()
    fig.add_bar(x=labels,y=values,marker_color=BLUE,marker_line_width=0,
                hovertemplate='<b>%{x}</b><br>%{y:,.0f} '+unit+'<extra></extra>')
    upper=max(values or [0])
    fig.update_layout(title=dict(text=title,font=dict(size=17,color=DARK)),
        height=height,margin=dict(l=10,r=12,t=55,b=38),
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        bargap=.22,showlegend=False,hovermode='closest',
        dragmode=False,clickmode='none',transition=dict(duration=0),
        font=dict(family='Arial, sans-serif',size=12,color='#536c80'),
        yaxis=dict(fixedrange=True,range=[0,max(1,upper*1.15)],rangemode='tozero',
                   tickformat=',.0f',gridcolor='#e1e9f2',zerolinecolor='#a7b8c8',
                   title=None),
        xaxis=dict(fixedrange=True,type='category',tickmode='array',
                   tickvals=labels[::sparse],ticktext=labels[::sparse],
                   showgrid=False,title=None))
    st.plotly_chart(fig,use_container_width=True,config=CHART_CONFIG)

def summary(vals,interval):
    nonzero=[x for x in vals if x>0]
    a,b,c=st.columns(3)
    a.metric('Total del període',f'{fmt(sum(vals))} palets')
    b.metric('Màxim per '+interval,f'{fmt(max(vals))} palets')
    c.metric('Mitjana productiva',f'{sum(nonzero)/len(nonzero):,.1f}' if nonzero else '0')

st.subheader('Anàlisi de producció')
st.caption('Escales des de zero · valors per interval · passa el cursor o toca les barres per consultar-les')

tab_h,tab_d,tab_m,tab_y,tab_r=st.tabs(['24 hores','30 dies','12 mesos','Anys','Canvis de bobina'])
with tab_h:
    bar_chart('Producció per hora',[f'{i:02d} h' for i in range(24)],hours,sparse=3)
    summary(hours,'hora')
with tab_d:
    bar_chart('Producció per dia',[f'Dia {i+1}' for i in range(30)],days,sparse=4)
    summary(days,'dia')
with tab_m:
    bar_chart('Producció mensual',[str(i+1) for i in range(12)],months,sparse=1)
    summary(months,'mes')
with tab_y:
    bar_chart('Producció acumulada anual',[str(y) for y in range(2017,2027)],annual,unit='palets acumulats',sparse=1)
    st.caption('Dades anuals fictícies ordenades cronològicament, amb l’any actual a la dreta.')
with tab_r:
    bar_chart('Palets entre canvis de bobina',[str(i+1) for i in range(24)],rolls,sparse=3)
    summary(rolls,'canvi')

st.subheader('Producció per programa')
left,right=st.columns([1.25,1],gap='large')
with left:
    labels=list(programs)
    vals=list(programs.values())
    fig=go.Figure(go.Pie(labels=labels,values=vals,hole=.64,
        sort=False,direction='clockwise',
        marker=dict(colors=['#166fb1','#4d9bd0','#91bedf','#c4d9eb','#e6edf4'],
                    line=dict(color='#ffffff',width=2)),
        textinfo='percent',textposition='inside',pull=0,rotation=0,
        hovertemplate='<b>%{label}</b><br>%{value:,.0f} palets · %{percent}<extra></extra>'))
    fig.update_layout(height=345,margin=dict(l=12,r=12,t=15,b=10),
        paper_bgcolor='rgba(0,0,0,0)',font=dict(color=DARK),
        dragmode=False,clickmode='none',transition=dict(duration=0),
        showlegend=False,
        annotations=[dict(text=f'<b>{fmt(sum(vals))}</b><br>palets',
                          x=.5,y=.5,font=dict(size=21,color=DARK),showarrow=False)])
    st.plotly_chart(fig,use_container_width=True,config=CHART_CONFIG)
with right:
    st.markdown('**Programes principals**')
    total=sum(programs.values())
    for name,value in sorted(programs.items(),key=lambda x:-x[1]):
        st.markdown(f'**{name}** · {fmt(value)} palets ({value/total:.1%})')
        st.progress(value/total)

st.info('Versió de demostració: totes les dades i els projectes són ficticis. '
        'Els CSV reals i la validació dels càlculs es tractaran en una versió posterior.')

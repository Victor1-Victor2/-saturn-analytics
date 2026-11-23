"""SATURN Analytics: demostració pública amb dades 100% sintètiques.
No llegeix fitxers reals, no desa dades i no exposa cap funció de pujada.
"""
import math
from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
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
st.markdown('<div class="hero"><h1>SATURN Analytics WEB</h1><p>Demostració pública · dades fictícies · sense connexió PLC</p></div>',unsafe_allow_html=True)
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
st.subheader('48 indicadors (valors ficticis)')
parts=[]
for label,val in kpis:
    parts.append(f'<div class="kpi"><div class="lbl">{html.escape(label)}</div><div class="val">{html.escape(val)}</div></div>')
st.markdown('<div class="kpis">'+''.join(parts)+'</div>',unsafe_allow_html=True)

st.subheader('Gràfics de producció (dades sintètiques)')
def chart(title, labels, values, ylabel='Palets / interval'):
    fig=go.Figure(go.Bar(x=labels,y=values,marker_color='#1772b5',hovertemplate='%{x}: %{y} palets<extra></extra>'))
    vmax=max(values) if values else 1
    fig.update_layout(title=title,autosize=True,height=320,margin=dict(l=10,r=10,t=48,b=20),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='white',yaxis=dict(range=[0,max(1,vmax*1.12)],title=ylabel,gridcolor='#e5eaf0'),xaxis=dict(title='Interval',tickangle=0),font=dict(size=12))
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})

hours=[max(0,round(8+7*math.sin((i+idx)*.64)+4*math.sin(i*1.9))) for i in range(24)]
days=[max(0,round(160+50*math.sin(i*.53+idx)+25*math.cos(i*.9))) for i in range(30)]
months=[max(0,round(2900+700*math.sin(i*.8+idx))) for i in range(12)]
rolls=[max(0,round(12+7*math.sin(i*.71+idx))) for i in range(24)]
chart('Últimes 24 hores',[str(i) for i in range(24)],hours)
chart('Últims 30 dies',[str(i+1) for i in range(30)],days)
chart('Últims 12 mesos',[str(i+1) for i in range(12)],months)
chart('Canvis de bobina',[str(i+1) for i in range(24)],rolls)
annual=[max(0,round(base*(i+1)/10)) for i in range(10)]
chart('Producció acumulada per anys',[str(y) for y in range(2017,2027)],annual,'Palets acumulats')
st.caption('Els gràfics d’aquesta demostració no validen els càlculs del CSV real. La versió privada necessitarà contrast amb Windows abans de publicar-se.')

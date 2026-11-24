import math
from datetime import datetime
from pathlib import Path
import csv
from historics_validats import increments_validats, resum_produccio_mensual
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(page_title='SATURN Analytics', page_icon='📊', layout='wide', initial_sidebar_state='collapsed')
st.markdown('''<style>
 .block-container{max-width:100%;padding:2.5rem 1rem .5rem}
.stApp{background:#f7f9fc}h1,h2,h3{color:#12385b}
[data-testid="stVerticalBlock"]{gap:.35rem}
.hero{background:#103454;color:white;padding:8px 14px;border-radius:8px;margin-bottom:2px}
.hero h1{color:white;font-size:1.15rem;margin:0}.hero p{display:none}
.kpi-board{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin:3px 0 5px}.kpi-column{display:grid;grid-template-rows:repeat(6,minmax(32px,auto));gap:3px;min-width:0}.kpi-section{color:#12385b;font-size:.75rem;font-weight:750;border-bottom:1px solid #1874b9;padding-bottom:2px}
.kpi{background:#e9f2fb;border-radius:5px;padding:3px 6px;min-width:0}
.kpi .lbl{color:#526c83;font-size:.65rem;line-height:1.15}.kpi .val{color:#12385b;font-size:.95rem;font-weight:750;line-height:1.2;overflow-wrap:anywhere}
@media(max-width:1000px){.kpi-board{grid-template-columns:1fr}.kpis{gap:8px}}
@media(max-width:550px){.block-container{padding:1rem .5rem}.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.kpi .val{font-size:1rem}}
</style>''',unsafe_allow_html=True)

import os, hmac, html
from storage import save, PATTERN
folder=Path(__file__).parent/'uploads'
folder.mkdir(exist_ok=True)
try:
    secret=st.secrets.get('MASTER_PASSWORD','')
except Exception:
    secret=os.environ.get('MASTER_PASSWORD','')
with st.sidebar.expander('MASTER · Administració'):
    if not st.session_state.get('master',False):
        with st.form('master_login'):
            password=st.text_input('Contrasenya MASTER',type='password')
            login=st.form_submit_button('Entrar')
        if login:
            if secret and hmac.compare_digest(password.encode('utf-8'),str(secret).encode('utf-8')):
                st.session_state.master=True
                st.rerun()
            else: st.error('Accés denegat o MASTER no configurat.')
    else:
        if st.button('Tancar sessió MASTER'):
            st.session_state.master=False
            st.rerun()
        st.warning('Emmagatzematge temporal: les captures poden desaparèixer quan es reinicia el servidor. La consulta és pública.')
        uploaded=st.file_uploader('Pujar CSV',type=['csv'],accept_multiple_files=True)
        if st.button('Guardar captures',disabled=not uploaded):
            for f in uploaded:
                try:
                    if save(folder,f.name,f.getvalue()): st.success('Captura incorporada')
                    else: st.info('Captura duplicada: no substituïda')
                except (ValueError,UnicodeError,KeyError,TypeError,OverflowError): st.error('CSV rebutjat: format o dades incompatibles')
        existing=sorted(p.name for p in folder.glob('datos_*.csv') if PATTERN.fullmatch(p.name))
        remove=st.multiselect('Captures per eliminar',existing)
        confirm=st.checkbox('Confirmo que vull eliminar les captures seleccionades')
        if st.button('Eliminar captures',disabled=not (remove and confirm)):
            for name in remove:
                if name in existing: (folder/name).unlink(missing_ok=True)
            st.rerun()
files=sorted(p for p in folder.glob('datos_*.csv') if PATTERN.fullmatch(p.name))
if not files:
    st.warning('No hi ha captures CSV.'); st.stop()
projects=sorted({p.name.split('_')[1] for p in files},key=int)
sel1=sel2=st.sidebar
project=sel1.selectbox('Número de projecte',projects,format_func=lambda x:'P'+x)
choices=[p for p in files if p.name.split('_')[1]==project][::-1]
selected=sel2.selectbox('Data i hora de captura',choices,format_func=lambda p:p.stem.split('_',2)[2].replace('_',' · '))
capture = selected.stem.split('_',2)[2].replace('_',' · ')
st.markdown(f'<div class="hero"><h1>SATURN Analytics · V1.4.2 <span style="float:right">P{html.escape(project)} · {html.escape(capture)}</span></h1></div>',unsafe_allow_html=True)
with selected.open(encoding='utf-8-sig',newline='') as f:
    rows=list(csv.DictReader(f))
byname={r['Nombre']:r['Valor'] for r in rows}
byindex={int(r['Índice']):r['Valor'] for r in rows if r['Índice'].isdigit()}
def num(i): return int(float(byindex[i]))
labels=['1.1 Projecte', '1.2 OEE sr', '1.3 Availability', '1.4 Quality', '1.5 Cadència', '1.6 OEE', '2.1 Palets totals · DB4000', '2.2 Pallets/hour LP', '2.3 Average P/H', '2.4 Palets dia', '2.5 Palets mes', '2.6 Prog +1000', '3.1 Voltes totals', '3.2 Wraps LP', '3.3 Average V/P', '3.4 Height detected', '3.5 Main Prog', '3.6 Palets Main', '4.1 Hores encesa', '4.2 Hores Auto', '4.3 Hores treball', '4.4 Hores alarma', '4.5 Hores No Auto', '4.6 Changes <3', '5.1 Registre', '5.2 Sector', '5.3 V/P Reg', '5.4 Tipus', '5.5 Max. T. Value', '5.6 Preestiro', '6.1 Program', '6.2 Single / Double', '6.3 Press plate', '6.4 Cover', '6.5 Wrapping RPM', '6.6 Wrapping tension', '7.1 Pallets 24CB', '7.2 Mitjana 24CB', '7.3 Mitjana canvis', '7.4 3<Changes<45', '7.5 45<Changes<80', '7.6 80>Changes', '8.1 Total emergències', '8.2 Pallets per alarma', '8.3 Barrera entrada', '8.4 Barrera sortida', '8.5 PLC On/Off', '8.6 Enfardat >180s']
keys=['Proyecto', 'OEE sr', 'Disponibilitat', 'Calidad', 'Cadencia', 'OEE', 'Palet Totales', 'Palet Hora LP', 'Average P/H', 'Palets Día', 'Palets Mes', 'Prog + 1000', 'Vueltas Totales', 'Vueltas LP', 'Average V/P', 'Height Detected', 'Main Prog', 'Palets Main', 'Horas Alimentada', 'Horas Auto', 'Horas Trabajo', 'Horas Alarma', 'Horas No Auto', 'Cambios < 3', 'Registro', 'Sector', 'V/P Reg', 'Tipo', 'Max. T. Value', 'Preestiro', 'Programa', 'Simple0/Doble1', 'Pisón', 'Cover', 'Rpm Enfardado', 'Tensión Enfardado', 'Palets 24CB', 'Average 24CB', 'Average Cambios', '3<Cambios<45', '45<Cambios<80', '80 > Cambios', 'Alarma 4', 'Palets/Alarma', 'Alarma 1', 'Alarma 2', 'Alarma 3', 'Alarma 5']
kpis=[(label,byname.get('KPI_'+key,'—')) for label,key in zip(labels,keys)]
kpis[0]=(labels[0],'P'+project)
kpis[6]=(labels[6],byindex[220])
kpis[25]=(labels[25],'No publicat')
import html
sections=[]
for start, heading in [(0, 'PRODUCTION & PERFORMANCE'), (24, 'MACHINE & PROCESS')]:
    columns=[]
    for offset in range(start,start+24,6):
        cards=[]
        for label,val in kpis[offset:offset+6]:
            cards.append(f'<div class="kpi"><div class="lbl">{html.escape(label)}</div><div class="val">{html.escape(val)}</div></div>')
        columns.append('<div class="kpi-column">'+''.join(cards)+'</div>')
    sections.append(f'<section><div class="kpi-section">{html.escape(heading)}</div><div class="kpis">'+''.join(columns)+'</div></section>')
st.markdown('<div class="kpi-board">'+''.join(sections)+'</div>',unsafe_allow_html=True)

# Dades de captures CSV.
BLUE='#1874b9'
DARK='#12385b'
LIGHT='#e7eff8'
CHART_CONFIG = dict(displayModeBar=False, scrollZoom=False, doubleClick=False, showTips=False, responsive=True)


db306=[num(i) for i in range(105,220)]
hours,ha= increments_validats(db306[1:25])
days,da= increments_validats(db306[59:90])
monthly=resum_produccio_mensual(db306)
months=monthly['increments'] if monthly else [0]*12
rolls,ra=increments_validats(db306[90:114])
raw=db306[49:59]; pivot=max(i for i,v in enumerate(raw) if v==max(raw))
annual=raw[pivot+1:]+raw[:pivot+1]
year=int(selected.stem.split('_')[2][:4])
all_programs=sorted([(f'Programa {i}',num(273+i)) for i in range(20)],key=lambda x:-x[1])
programs=dict((k,v) for k,v in all_programs[:4] if v>0)
other=sum(v for k,v in all_programs[4:])
if other: programs['Altres']=other
if not programs: programs={'Sense producció':0}

def fmt(n):
    return f'{n:,.0f}'.replace(',','.')

def bar_chart(title, labels, values, unit='palets', height=150, sparse=1):
    fig=go.Figure()
    fig.add_bar(x=labels,y=values,marker_color=BLUE,marker_line_width=0,
                hovertemplate='<b>%{x}</b><br>%{y:,.0f} '+unit+'<extra></extra>')
    upper=max(values or [0])
    fig.update_layout(title=dict(text=title,font=dict(size=12,color=DARK)),
        height=height,margin=dict(l=8,r=8,t=27,b=25),
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        bargap=.22,showlegend=False,hovermode='closest',
        dragmode=False,clickmode='none',transition=dict(duration=0),
        font=dict(family='Arial, sans-serif',size=9,color='#536c80'),
        yaxis=dict(fixedrange=True,range=[0,max(1,upper*1.15)],rangemode='tozero',
                   tickformat=',.0f',gridcolor='#e1e9f2',zerolinecolor='#a7b8c8',
                   title=None),
        xaxis=dict(fixedrange=True,type='category',tickmode='array',
                   tickvals=labels[::sparse],ticktext=labels[::sparse],
                   showgrid=False,title=None))
    st.plotly_chart(fig,use_container_width=True,config=CHART_CONFIG)

def summary(vals,interval):
    nonzero=[x for x in vals if x>0]
    avg=sum(nonzero)/len(nonzero) if nonzero else 0
    st.caption(f'Total {fmt(sum(vals))} · Màx. {fmt(max(vals))} · Mitjana {avg:.1f}')

view=st.radio('Gràfiques', ['Producció · hores / dies / mesos','Històric i procés · anys / bobines / programes'],horizontal=True,label_visibility='collapsed')
if view.startswith('Producció'):
    tab_h,tab_d,tab_m=st.columns(3)
    with tab_h:
        bar_chart('Producció per hora',[f'{i:02d} h' for i in range(24)],hours,sparse=3)
        summary(hours,'hora')
    with tab_d:
        bar_chart('Producció per dia',[f'Dia {i+1}' for i in range(len(days))],days,sparse=4)
        summary(days,'dia')
    with tab_m:
        bar_chart('Producció mensual',[str(i+1) for i in range(12)],months,sparse=1)
        summary(months,'mes')
else:
    tab_y,tab_r,tab_p=st.columns(3)
    with tab_y:
        bar_chart('Producció acumulada anual',[str(y) for y in range(year-9,year+1)],annual,unit='palets acumulats',sparse=1)
        st.caption('Acumulats circulars: màxim a la dreta, assignat a l’any de captura.')
    with tab_r:
        bar_chart('Palets entre canvis de bobina',[str(i+1) for i in range(24)],rolls,sparse=3)
        summary(rolls,'canvi')
    
    with tab_p:
        labels=list(programs)
        vals=list(programs.values())
        fig=go.Figure(go.Pie(labels=labels,values=vals,hole=.64,
            sort=False,direction='clockwise',
            marker=dict(colors=['#166fb1','#4d9bd0','#91bedf','#c4d9eb','#e6edf4'],
                        line=dict(color='#ffffff',width=2)),
            textinfo='percent',textposition='inside',pull=0,rotation=0,
            hovertemplate='<b>%{label}</b><br>%{value:,.0f} palets · %{percent}<extra></extra>'))
        fig.update_layout(height=150,title=dict(text="Producció per programa",font=dict(size=12)),margin=dict(l=8,r=8,t=27,b=5),
            paper_bgcolor='rgba(0,0,0,0)',font=dict(color=DARK),
            dragmode=False,clickmode='none',transition=dict(duration=0),
            showlegend=False,
            annotations=[dict(text=f'<b>{fmt(sum(vals))}</b><br>palets',
                              x=.5,y=.5,font=dict(size=13,color=DARK),showarrow=False)])
        st.plotly_chart(fig,use_container_width=True,config=CHART_CONFIG)
        st.caption(' · '.join(f'{name}: {fmt(value)}' for name,value in programs.items()))

st.caption('Captures històriques: no són dades en directe. Els increments amb base absent o lectures antigues es tracten segons el lector de Windows; cal validar els gràfics amb els informes originals.')

import csv, io, re, hashlib, os, tempfile
from pathlib import Path
from datetime import datetime
from math import isfinite
PATTERN=re.compile(r'datos_(\d{1,10})_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})(?:_[\w-]+)?\.csv',re.I)
FIELDS=['Índice','indice2','Nombre','Valor']
def clean(name, raw):
    m=PATTERN.fullmatch(name)
    if not m or len(raw)>2_000_000: raise ValueError('Nom o mida de fitxer no vàlids')
    datetime.strptime(m[2],'%Y-%m-%d_%H-%M-%S')
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    if reader.fieldnames!=FIELDS: raise ValueError('Format CSV incompatible')
    rows=list(reader)
    if not rows or len(rows)>2000 or any(None in r or any(v is None for v in r.values()) for r in rows): raise ValueError('Registres incorrectes')
    idx={int(r['Índice']):r['Valor'] for r in rows if r['Índice'].isdigit()}
    for i in list(range(105,221))+list(range(273,293)):
        if not isfinite(float(idx.get(i,'nan'))): raise ValueError('Falten registres numèrics necessaris')
    for r in rows:
        n=r['Nombre'].casefold().strip()
        if n in ('cliente','db1111_2','client','kpi_cliente'): r['Valor']='RD_Analytics'
        elif 'observa' in n or n in ('técnico','tecnico','sector cliente','kpi_sector','db1111_3','db1111_6','db1111_8','db1111_9','db1111_10','db1111_11'): r['Valor']=''
        elif n in ('num proyecto','numero proyecto','kpi_proyecto') and r['Valor'].strip().lstrip('0')!=m[1].lstrip('0'): raise ValueError('Projecte inconsistent')
    out=io.StringIO(newline=''); w=csv.DictWriter(out,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    return f'datos_{int(m[1])}_{m[2]}.csv',out.getvalue().encode('utf-8')
def save(folder,name,raw):
    name,data=clean(name,raw); folder.mkdir(parents=True,exist_ok=True); dest=folder/name
    try:
        with dest.open('xb') as f: f.write(data)
    except FileExistsError: return False
    return True

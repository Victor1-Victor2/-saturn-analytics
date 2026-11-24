"""Reconstrucció conservadora de diferències de comptadors acumulatius.

La posició temporal i el primer valor han de ser verificats amb el PLC.
No escriu cap valor al PLC ni inventa producció als períodes sense mostra.
"""
from math import isfinite

def reconstruir_circular(registres):
    """Reconstueix la cronologia començant després del darrer màxim.

    El valor més alt és la lectura més recent en un comptador creixent.
    Les posicions posteriors al màxim són les més antigues del búfer.
    Les lectures obsoletes es mantenen constants, sense modificar el PLC.
    """
    raw=list(registres); n=len(raw)
    if not n: return [],[],[]
    def numero(v):
        try:
            x=float(v)
            return x if isfinite(x) and x>=0 else None
        except (ValueError,TypeError,OverflowError): return None
    nums=[numero(x) for x in raw]
    valid=[(i,v) for i,v in enumerate(nums) if v is not None]
    if not valid: return [0]*n,[0]*n,[{'tipus':'sense_dades'}]
    peak=max(v for _,v in valid)
    pivot=max(i for i,v in valid if v==peak)
    order=[(pivot+1+j)%n for j in range(n)]
    corrected=[0]*n; diffs=[0]*n; avisos=[]; previous=None
    for i in order:
        v=nums[i]
        if v is None or (previous is not None and v<previous):
            corrected[i]=previous if previous is not None else 0
            avisos.append({'posicio':i+1,'tipus':'registre_antic_o_invalid',
                           'original':raw[i],'corregit':corrected[i]})
        else:
            corrected[i]=v
            if previous is not None: diffs[i]=max(0,v-previous)
            previous=v
    diffs[order[0]]=0 # manca la base de la mostra més antiga
    def fmt(v): return int(v) if float(v).is_integer() else v
    return [fmt(v) for v in corrected],[fmt(v) for v in diffs],avisos


def increments_validats(registres):
    """Diferències circulars amb correcció de lectures antigues."""
    _,increments,avisos=reconstruir_circular(registres)
    return increments,avisos

def acumulados_corregidos(registres):
    """Corrige lecturas obsoletas; requiere orden cronológico previo."""
    from math import isfinite
    out=[];avisos=[];ultimo=None
    for i,raw in enumerate(registres):
        try:
            v=float(raw)
            if not isfinite(v) or v<0: raise ValueError()
        except (ValueError,TypeError,OverflowError):
            avisos.append((i,"invalido"))
            out.append(ultimo if ultimo is not None else 0)
            continue
        if ultimo is not None and v<ultimo:
            avisos.append((i,"antic"))
            out.append(ultimo)
        else:
            ultimo=v;out.append(v)
    return out,avisos


def corregir_hasta_maximo(registres):
    """Corrige solo posiciones anteriores/al máximo, nunca posteriores.

    Se presupone que la secuencia está ordenada por período (mes 1..12).
    El último máximo marca el final del tramo histórico validable.
    Los meses posteriores conservan el dato PLC aunque sea inferior.
    """
    from math import isfinite
    valores = list(registres)
    validos=[]
    for i, raw in enumerate(valores):
        try:
            v=float(raw)
            if isfinite(v) and v>=0: validos.append((i,v))
        except (ValueError, TypeError, OverflowError):
            pass
    if not validos: return valores, [], None
    # último máximo en caso de empate: evita dejar sin corregir un período ya leído
    maximo=max(v for _,v in validos)
    fin=max(i for i,v in validos if v==maximo)
    corregidos=valores.copy()
    avisos=[]
    anterior=None
    for i in range(fin+1):
        try:
            v=float(valores[i])
            if not isfinite(v) or v<0: raise ValueError()
        except (ValueError, TypeError, OverflowError):
            if anterior is not None:
                corregidos[i]=anterior
                avisos.append({'posicio':i+1,'tipus':'invalido','corregit':anterior})
            continue
        if anterior is not None and v<anterior:
            corregidos[i]=anterior
            avisos.append({'posicio':i+1,'tipus':'registre_antic','original':v,'corregit':anterior})
        else:
            anterior=v
    return corregidos, avisos, fin


def increments_fins_maxim(registres):
    """Retorna increments sense calcular producció dels mesos futurs."""
    corr, avisos, fin = corregir_hasta_maximo(registres)
    diffs=[0]*len(corr)
    if fin is None: return diffs, avisos, fin
    for i in range(1,fin+1):
        try:
            diffs[i]=max(0,float(corr[i])-float(corr[i-1]))
        except (ValueError, TypeError, OverflowError):
            pass
    return [int(x) if float(x).is_integer() else x for x in diffs], avisos, fin


def preparar_meses_con_base_anual(registres, acumulado_anterior=None):
    """Serie 1..12. Anterior año es base para enero y meses aún futuros.

    Si falta la base, enero es desconocido (no se inventa producción).
    El máximo marca último mes con lectura actual; después se usa la base
    del año anterior sólo para visualizar, sin atribuir producción.
    """
    from math import isfinite
    corr, avisos, fin = corregir_hasta_maximo(registres)
    if fin is None:
        return list(registres), [0]*len(registres), None, avisos
    try:
        base = float(acumulado_anterior)
        if not isfinite(base) or base <= 0 or base > float(corr[0]):
            base = None
    except (ValueError, TypeError, OverflowError):
        base = None
    incrementos = [0]*len(corr)
    if base is not None:
        incrementos[0] = max(0,float(corr[0])-base)
    else:
        avisos.append({'posicio':1,'tipus':'sense_base_any_anterior'})
    for i in range(1,fin+1):
        incrementos[i] = max(0,float(corr[i])-float(corr[i-1]))
    if base is not None:
        for i in range(fin+1,len(corr)):
            corr[i] = base
    # Si no hi ha base, no inventar acumulat per als mesos futurs.
    return corr, [int(v) if float(v).is_integer() else v for v in incrementos], fin, avisos


def resum_produccio_mensual(db306):
    """Única font del KPI 2.5 i de l'estimació de la gràfica mensual."""
    if len(db306) < 53:
        return None
    try:
        base = float(db306[52])
    except (ValueError, TypeError, OverflowError):
        base = None
    visibles, increments, ultim, avisos = preparar_meses_con_base_anual(db306[37:49], base)
    if ultim is None:
        return None
    observats = increments[:ultim+1]
    estimacio = round(sum(observats)/len(observats)) if observats else None
    return {'acumulats':visibles,'increments':increments,'ultim':ultim,'estimacio':estimacio,'avisos':avisos}


def produccio_any_actual(db306):
    """Diferència entre el registre anual actual i el de l'any anterior."""
    from datetime import datetime
    idx = datetime.now().year - 2022 + 49
    if idx <= 49 or idx >= len(db306):
        return None
    try:
        actual, anterior = float(db306[idx]), float(db306[idx-1])
        if actual >= anterior > 0:
            return int(actual-anterior)
    except (TypeError, ValueError, OverflowError):
        pass
    return None

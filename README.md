# SATURN Analytics — Demo V1.2

Demostració pública amb dades **100% sintètiques**. No connecta a PLC ni accepta CSV reals. No mostra noms de clients ni marques d’empresa.

## Novetats
- Gràfics amb eix vertical des de zero, etiquetes llegibles i informació en passar el cursor.
- Pestanyes per a 24 hores, 30 dies, 12 mesos, anys i canvis de bobina.
- Gràfic circular tipus donut amb els programes més importants, percentatges i totals.
- Resums per interval i disseny adaptable al mòbil.
- 48 KPI de demostració, sense canviar els valors de la demo anterior.

## Publicació
Substitueix `app.py`, `requirements.txt`, `README.md` i `.gitignore` al repositori de GitHub. Streamlit Community Cloud tornarà a desplegar l’aplicació automàticament.

## Execució local
`pip install -r requirements.txt`

`streamlit run app.py`


V1.2.1: eixos bloquejats, zoom i arrossegament desactivats, donut fix sense llegenda interactiva. Es mantenen les dades fictícies i els KPI.

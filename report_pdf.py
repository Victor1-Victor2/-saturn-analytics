from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor, white
import math

def make_pdf(project,capture,kpis,specs,programs):
    out=BytesIO(); w,h=landscape(A4); c=canvas.Canvas(out,pagesize=(w,h)); blue=HexColor('#548bb9'); dark=HexColor('#173650'); pale=HexColor('#edf3f8')
    def header(page,title):
        c.setFillColor(dark); c.roundRect(24,h-77,w-48,53,12,fill=1,stroke=0); c.setFillColor(white); c.setFont('Helvetica-Bold',19); c.drawString(38,h-45,'RD37_4U  |  SATURN Analytics'); c.setFont('Helvetica',10); c.drawString(38,h-62,f'P{project}  |  {capture}'); c.setFillColor(dark); c.setFont('Helvetica-Bold',12); c.drawString(28,h-98,title); c.setFont('Helvetica',9); c.drawRightString(w-28,18,f'{page} / 2')
    header(1,'MACHINE PERFORMANCE')
    cw=(w-56)/8
    for i,(label,val) in enumerate(kpis):
        x=28+(i//6)*cw; y=h-165-(i%6)*65
        c.setFillColor(pale); c.roundRect(x,y,cw-5,58,8,fill=1,stroke=0); c.setFillColor(dark); c.setFont('Helvetica',7); c.drawString(x+5,y+41,label[:29]); c.setFont('Helvetica-Bold',12 if len(str(val))<12 else 8); c.drawString(x+5,y+19,str(val)[:23])
    c.showPage(); header(2,'PRODUCTION ANALYTICS')
    for i,(title,fig,detail) in enumerate(specs):
        x=28+(i%3)*(w-56)/3; y=h-315-(i//3)*220; bw=(w-56)/3-8; bh=207
        c.setFillColor(pale); c.roundRect(x,y,bw,bh,9,fill=1,stroke=0); c.setFillColor(dark); c.setFont('Helvetica-Bold',10); c.drawString(x+9,y+bh-17,title)
        if i==5:
            total=sum(v for _,v in programs)
            for j,(name,v) in enumerate([(n,v) for n,v in programs[:4] if v>0]):
                cx=x+bw*(.25+.5*(j%2)); cy=y+bh-63-78*(j//2); r=27
                c.setStrokeColor(HexColor('#dce6ef')); c.setLineWidth(6); c.circle(cx,cy,r,stroke=1,fill=0); c.setStrokeColor(blue); c.arc(cx-r,cy-r,cx+r,cy+r,90,-360*v/total); c.setFillColor(dark); c.setFont('Helvetica-Bold',9); c.drawCentredString(cx,cy,str(v)); c.setFont('Helvetica',7); c.drawCentredString(cx,cy-10,name)
        else:
            trace=fig.data[0]; vals=list(trace.y); labs=list(trace.x); maximum=max(1,max(vals)); px=x+27; py=y+37; pw=bw-37; ph=132
            c.setStrokeColor(HexColor('#cbd9e5')); c.setLineWidth(.5); c.line(px,py,px+pw,py); c.setFillColor(dark); c.setFont('Helvetica',7); c.drawString(x+3,py+ph,str(maximum)); c.drawString(x+12,py,'0')
            step=pw/max(1,len(vals)); c.setFillColor(blue)
            if i==3:
                path=c.beginPath(); path.moveTo(px,py)
                for j,v in enumerate(vals): path.lineTo(px+(j+.5)*step,py+max(0,v)/maximum*ph)
                path.lineTo(px+pw,py); path.close(); c.setFillColor(HexColor('#b8d2e7')); c.drawPath(path,fill=1,stroke=0)
            else:
                for j,v in enumerate(vals):
                    c.setFillColor(HexColor('#d9b17d') if i==4 and 0<v<3 else blue); c.rect(px+j*step+1,py,max(1,step-2),max(0,v)/maximum*ph,fill=1,stroke=0)
            if i in (1,4):
                nz=[v for v in vals if v>0]
                if nz:
                    yy=py+sum(nz)/len(nz)/maximum*ph; c.setStrokeColor(dark); c.setDash(3,3); c.line(px,yy,px+pw,yy); c.setDash()
            c.setFillColor(dark); c.setFont('Helvetica',7)
            for j in range(0,len(labs),max(1,math.ceil(len(labs)/5))): c.drawCentredString(px+(j+.5)*step,py-10,str(labs[j]))
            c.drawString(x+7,y+8,detail[:75])
    c.showPage(); c.save(); return out.getvalue()

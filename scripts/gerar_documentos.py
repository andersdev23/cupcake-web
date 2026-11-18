"""Gera relatório e instrumento de avaliação. Requer reportlab apenas para gerar PDFs."""
from pathlib import Path
import html
import re
import sqlite3
import sys
import tempfile

from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Ellipse, Polygon

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'pdf'
OUT.mkdir(parents=True, exist_ok=True)
INK = colors.HexColor('#3d2114')
PINK = colors.HexColor('#a6334d')
PALE = colors.HexColor('#f9edf0')
GRAY = colors.HexColor('#51565e')
RULE = colors.HexColor('#ded2cc')
W, H = A4
TEXTW = W - 110
fontroot = Path('C:/Windows/Fonts')
pdfmetrics.registerFont(TTFont('Body', str(fontroot / 'arial.ttf')))
pdfmetrics.registerFont(TTFont('BodyBold', str(fontroot / 'arialbd.ttf')))
pdfmetrics.registerFont(TTFont('BodyItalic', str(fontroot / 'ariali.ttf')))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='BodyBold', italic='BodyItalic', boldItalic='BodyBold')
ST = getSampleStyleSheet()
ST.add(ParagraphStyle(name='Text', fontName='Body', fontSize=9.8, leading=14, textColor=INK, spaceAfter=7))
ST.add(ParagraphStyle(name='TitleMain', fontName='BodyBold', fontSize=30, leading=36, textColor=INK, spaceAfter=20))
ST.add(ParagraphStyle(name='Section', fontName='BodyBold', fontSize=18, leading=23, textColor=INK, spaceAfter=12, spaceBefore=8, keepWithNext=True))
ST.add(ParagraphStyle(name='Sub', fontName='BodyBold', fontSize=12, leading=17, textColor=PINK, spaceBefore=14, spaceAfter=7, keepWithNext=True))
ST.add(ParagraphStyle(name='SmallText', fontName='Body', fontSize=8.5, leading=12, textColor=GRAY, spaceAfter=8))
ST.add(ParagraphStyle(name='Cell', fontName='Body', fontSize=8.3, leading=11, textColor=INK))
ST.add(ParagraphStyle(name='HeadCell', fontName='BodyBold', fontSize=8.3, leading=11, textColor=colors.white))


def inline(text):
    text = html.escape(text).replace('—', '-').replace('–', '-')
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`([^`]+)`', r'<font name="BodyBold">\1</font>', text)
    text = re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'\1', text)
    return text


def p(text, style='Text'):
    return Paragraph(inline(text), ST[style])


def footer(c, doc):
    c.saveState()
    c.setStrokeColor(RULE); c.line(55, 43, W-55, 43)
    c.setFillColor(GRAY); c.setFont('Body', 8)
    c.drawString(55, 29, 'Sweet Bloom | Anderson Alves de Souza | RGM 37137794')
    c.drawRightString(W-55, 29, str(doc.page))
    c.restoreState()


def table(rows, widths=None):
    cells = [[Paragraph(inline(str(v)), ST['HeadCell' if i==0 else 'Cell']) for v in row] for i,row in enumerate(rows)]
    if widths is None:
        n = len(rows[0]); widths = [TEXTW/n]*n
        if n==2: widths=[TEXTW*.26,TEXTW*.74]
        if n==3: widths=[TEXTW*.17,TEXTW*.34,TEXTW*.49]
    t=Table(cells, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),INK), ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),9), ('RIGHTPADDING',(0,0),(-1,-1),9),
        ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#faf7f5')]),
        ('LINEBELOW',(0,0),(-1,-1),.35,RULE)]))
    return t


def label(d,x,y,text,size=9,bold=False,anchor='middle'):
    d.add(String(x,y,text,fontName='BodyBold' if bold else 'Body',fontSize=size,fillColor=INK,textAnchor=anchor))


def box(d,x,y,w,h,title,lines=()):
    d.add(Rect(x,y,w,h,rx=5,ry=5,strokeColor=RULE,fillColor=colors.white))
    d.add(Rect(x,y+h-26,w,26,strokeColor=RULE,fillColor=PALE))
    label(d,x+w/2,y+h-17,title,9,True)
    for i,line in enumerate(lines): label(d,x+9,y+h-42-i*14,line,8,anchor='start')


def arrow(d,x1,y1,x2,y2,caption=None):
    import math
    d.add(Line(x1,y1,x2,y2,strokeColor=PINK,strokeWidth=1))
    a=math.atan2(y2-y1,x2-x1); length=6
    pts=[x2,y2,x2-length*math.cos(a-.4),y2-length*math.sin(a-.4),x2-length*math.cos(a+.4),y2-length*math.sin(a+.4)]
    d.add(Polygon(pts,fillColor=PINK,strokeColor=PINK))
    if caption: label(d,(x1+x2)/2,(y1+y2)/2+6,caption,7)


def diagram(kind):
    if kind=='architecture':
        d=Drawing(TEXTW,155)
        names=[('Views',['HTML, CSS e JS']),('Controller',['HTTP e sessão']),('Service',['Regras']),('Database',['SQLite'])]
        for i,(name,lines) in enumerate(names):
            x=i*123;box(d,x,43,112,75,name,lines)
            if i<3: arrow(d,x+112,80,x+123,80)
        label(d,TEXTW/2,18,'Separação inspirada em MVC com camada de serviço',9)
        return d
    if kind=='usecase':
        d=Drawing(TEXTW,240)
        label(d,48,211,'Cliente',11,True);label(d,414,211,'Administrador',11,True)
        left=['Consultar catálogo','Gerenciar carrinho','Registrar pedido'];right=['Autenticar','Consultar pedidos','Atualizar status','Manter catálogo']
        for i,text in enumerate(left):
            y=154-i*54;d.add(Ellipse(130,y,83,20,fillColor=PALE,strokeColor=RULE));label(d,130,y-3,text)
            d.add(Line(48,195,62,y+7,strokeColor=GRAY))
        for i,text in enumerate(right):
            y=165-i*48;d.add(Ellipse(343,y,86,19,fillColor=PALE,strokeColor=RULE));label(d,343,y-3,text)
            d.add(Line(414,195,421,y+5,strokeColor=GRAY))
        return d
    if kind=='classes':
        d=Drawing(TEXTW,250)
        box(d,0,118,225,126,'ShopHandler',['do_GET / do_POST / do_PATCH','payload / authenticated','respond / static_allowed'])
        box(d,260,118,225,126,'ShopService',['quote / place_order / orders','change_status / update_product'])
        box(d,0,0,225,88,'AdminSessions',['login(password, ip)','find(token)'])
        box(d,260,0,225,88,'Database',['initialize / connect','products / order'])
        arrow(d,225,181,260,181,'delega');arrow(d,112,118,112,88);arrow(d,372,118,372,88)
        return d
    if kind=='sequence':
        d=Drawing(TEXTW,290);xs=[44,167,293,429];titles=['Cliente','Checkout JS','ShopService','SQLite']
        for x,t in zip(xs,titles):
            label(d,x,273,t,9,True);d.add(Line(x,255,x,20,strokeColor=RULE,strokeDashArray=[3,3]))
        steps=[(0,1,'Confirmar',234),(1,2,'POST /api/orders via controller',204),(2,3,'BEGIN; verificar chave',174),(2,3,'Validar e gravar dados',144),(3,2,'COMMIT e pedido',114),(2,1,'201 novo / 200 repetido',84),(1,0,'Recibo e número real',54)]
        for a,b,t,y in steps:arrow(d,xs[a],y,xs[b],y,t)
        return d
    if kind=='activity':
        d=Drawing(TEXTW,150)
        for i,t in enumerate(['Recebido','Em preparo','Saiu para entrega','Entregue']):
            box(d,i*123,75,112,44,t)
            if i<3:arrow(d,i*123+112,96,(i+1)*123,96)
        box(d,80,0,175,44,'Cancelado')
        arrow(d,55,75,120,44);arrow(d,178,75,200,44)
        return d
    if kind=='er':
        d=Drawing(TEXTW,430)
        box(d,0,295,215,123,'customers',['id PK; phone UNIQUE','name; email'])
        box(d,270,295,215,123,'addresses',['id PK; customer_id FK','street; neighborhood','postal_code; complement'])
        box(d,0,118,215,133,'orders',['id PK; request_key UNIQUE','customer_id FK; address_id FK','payment; status; version','valores; destinatário; data'])
        box(d,270,118,215,133,'order_items',['id PK; order_id FK','product_id FK; quantity','product_name; unit_price_cents','UNIQUE(order_id, product_id)'])
        box(d,0,0,215,77,'order_history',['id PK; order_id FK','status; changed_at'])
        box(d,270,0,215,77,'products',['id PK; slug UNIQUE','name; price_cents; active'])
        arrow(d,215,354,270,354,'1:N');arrow(d,105,295,105,251,'1:N')
        arrow(d,310,295,167,251,'1:N');arrow(d,215,184,270,184,'1:N')
        arrow(d,105,118,105,77,'1:N');arrow(d,378,77,378,118,'1:N')
        return d
    return Spacer(1,1)


def markdown_story(path):
    lines=path.read_text(encoding='utf-8').splitlines(); story=[]; i=0; section=''
    while i<len(lines):
        line=lines[i].strip()
        if not line: i+=1;continue
        if line.startswith('```'):
            lang=line[3:];block=[];i+=1
            while i<len(lines) and not lines[i].strip().startswith('```'):block.append(lines[i]);i+=1
            if lang=='mermaid':
                mapping={'Arquitetura':'architecture','Casos':'usecase','Classes':'classes','Sequência':'sequence','Atividade':'activity','Modelo conceitual':'er'}
                key=next((v for k,v in mapping.items() if section.startswith(k)),None)
                if key:story.extend([diagram(key),Spacer(1,12)])
            else:
                for l in block:story.append(p(l,'SmallText'))
            i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                row=[v.strip() for v in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[: -]+',v or '-') for v in row):rows.append(row)
                i+=1
            story.extend([table(rows),Spacer(1,12)]);continue
        if line.startswith('# '):story.append(p(line[2:],'Section'));section=line[2:]
        elif line.startswith('## '):section=line[3:];story.append(p(section,'Sub'))
        elif line.startswith('- ') or re.match(r'^\d+\. ',line):
            if line.startswith('- [ ]'):line='[  ] '+line[5:]
            story.append(p(line));i+=1;continue
        else:
            block=[line];i+=1
            while i<len(lines) and lines[i].strip() and not lines[i].strip().startswith(('#','|','```','- ')) and not re.match(r'^\d+\. ',lines[i].strip()):
                block.append(lines[i].strip());i+=1
            text=' '.join(block)
            if text.startswith('- [ ]'):text='[  ] '+text[5:]
            story.append(p(text));continue
        i+=1
    return story


def create_report():
    story=[Spacer(1,42),p('Universidade Positivo (UP)','Sub'),p('Anderson Alves de Souza','Text'),p('RGM 37137794','Text'),Spacer(1,78),p('Sweet Bloom','TitleMain'),p('Evolução da loja de cupcakes para o Projeto Integrador II','Section'),p('Relatório técnico de implementação, modelagem e validação','Text'),Spacer(1,50),p('Tutora: Fabiana Sabai Rodrigues Bastos','Text'),p('17 de novembro de 2026','Text'),Spacer(1,45),p('Este documento registra a implementação e as verificações técnicas realizadas. Avaliações de cinco participantes e vídeo são entregas separadas; sua realização não é presumida neste relatório.','SmallText'),PageBreak()]
    for name in ['01_planejamento.md','02_modelagem.md','04_testes_resultados.md','05_manual_video_entrega.md']:
        story+=markdown_story(ROOT/'docs'/name);story.append(PageBreak())
    story += [p('Evidências da interface','Section'),p('Capturas da execução com dados fictícios no servidor de teste. As imagens completas estão em docs/evidencias/. O número do pedido pertence ao banco isolado de validação.','Text')]
    for name,title in [('pedido-registrado.png','Recibo após gravação real'),('admin-pedidos.png','Gestão de pedidos e histórico'),('admin-catalogo.png','Manutenção do catálogo')]:
        story.append(p(title,'Sub'))
        im=Image(str(ROOT/'docs/evidencias'/name));scale=min(TEXTW/im.imageWidth,590/im.imageHeight);im.drawWidth=im.imageWidth*scale;im.drawHeight=im.imageHeight*scale
        story.extend([im,PageBreak()])
    story += [p('Referências e rastreabilidade','Section'),p('Código original do PI I: https://github.com/andersdev23/cupcake-web, revisão 1c64815. Continuidade com o PI I confirmada pelo autor.','Text'),p('Versão estática anterior: https://cupcake-web-eight.vercel.app/. Não representa automaticamente o servidor Python desta evolução.','Text'),p('Enunciado fornecido pelo autor: PITESoftwareII.pdf, orientações de desenvolvimento, modelagem, testes, avaliações externas, vídeo e entrega. O modelo oficial do AVA deve prevalecer na formatação da submissão.','Text'),p('Fontes tipográficas da interface: Playfair Display e DM Sans, Google Fonts, com licenças OFL incluídas em assets/fonts/.','Text'),p('Documentação e código desta evolução: branch pi2/evolucao-sweet-bloom. A existência da branch local não comprova publicação; verificar o link remoto antes de submeter.','Text'),p('Situação da avaliação externa','Sub'),p('Na preparação desta versão, o autor declarou ainda não ter reunido os cinco avaliadores. O instrumento em branco foi preparado; não há resultados externos, depoimentos ou alterações atribuídas a participantes. Após a coleta, anexar relatório consolidado real e evidências.','Text')]
    doc=SimpleDocTemplate(str(OUT/'relatorio_tecnico_sweet_bloom_pi2.pdf'),pagesize=A4,rightMargin=55,leftMargin=55,topMargin=52,bottomMargin=60,title='Sweet Bloom - Relatório técnico PI II',author='Anderson Alves de Souza')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)


def create_forms():
    path=OUT/'formularios_cinco_avaliadores.pdf';c=canvas.Canvas(str(path),pagesize=A4)
    c.setTitle('Sweet Bloom - Instrumento de avaliação em branco');c.setAuthor('Anderson Alves de Souza')
    expected=[]
    def txt(x,y,text,size=10,bold=False,color=INK):
        c.setFillColor(color);c.setFont('Helvetica-Bold' if bold else 'Helvetica',size);c.drawString(x,y,text)
    def field(name,x,y,w,h=23,multiline=False):
        expected.append(name)
        c.acroForm.textfield(name=name,tooltip=name.replace('_',' '),x=x,y=y,width=w,height=h,fontName='Helvetica',fontSize=9,borderWidth=.6,borderStyle='solid',borderColor=RULE,fillColor=colors.white,textColor=INK,fieldFlags='multiline' if multiline else '',value='',forceBorder=True,maxlen=1500 if multiline else 160)
    funcs=['Consultar produtos e preços','Adicionar e alterar carrinho','Remover produto do carrinho','Preencher e validar dados','Conferir desconto PIX e total','Registrar e receber número','Consultar pedido no painel','Atualizar status e histórico','Alterar preço/disponibilidade']
    for num in range(1,6):
        txt(48,790,'Sweet Bloom - avaliação por participante',17,True)
        txt(48,769,f'Participante {num} de 5 | Instrumento em branco',10,True,PINK)
        txt(48,750,'Preencha após testar. Use dados fictícios nos pedidos. Não informe senhas.',9)
        txt(48,721,'Nome do avaliador');field(f'p{num}_nome',48,690,499)
        txt(48,674,'Perfil (colega/profissional)');field(f'p{num}_perfil',48,643,330)
        txt(394,674,'Data do teste');field(f'p{num}_data',394,643,153)
        txt(48,622,'Versão/link/ambiente testado');field(f'p{num}_versao',48,591,499)
        txt(48,572,'F = funcionou | NF = não funcionou | NT = não testado',9,True)
        txt(48,556,'Se NF ou NT, explique o motivo no campo abaixo.',9)
        for i,func in enumerate(funcs):
            y=526-i*27;txt(48,y+5,func,9)
            name=f'p{num}_funcao_{i+1}';expected.append(name)
            c.acroForm.choice(name=name,tooltip=func,x=435,y=y,width=112,height=23,options=['Selecionar','F','NF','NT'],value='Selecionar',fontName='Helvetica',fontSize=9,borderWidth=.6,borderColor=RULE,fillColor=colors.white,textColor=INK,fieldFlags='combo',forceBorder=True)
        txt(48,280,'Falhas / não testados: função, motivo e como reproduzir',9,True);field(f'p{num}_motivos',48,211,499,59,True)
        txt(48,194,'Sugestões e comentários de usabilidade',9,True);field(f'p{num}_sugestoes',48,125,499,59,True)
        txt(48,107,'Referência de capturas/anexos (se houver)',9);field(f'p{num}_evidencias',48,75,499)
        txt(48,42,'Anderson Alves de Souza | RGM 37137794 | Não é um resultado preenchido.',8,color=GRAY)
        txt(520,42,str(num),8,color=GRAY);c.showPage()
    txt(48,790,'Consolidação pelo autor',18,True)
    txt(48,766,'Preencher somente após receber as cinco avaliações reais.',10,True,PINK)
    for name,title,y,height in [('participantes','Nomes e datas das cinco avaliações',723,90),('resultados','Resumo das funções: funcionou / falhou / não testado',582,90),('correcoes','Sugestões adotadas, correções e evidências do novo teste',441,110),('nao_adotadas','Sugestões não adotadas e justificativa',280,90),('anexos','Referências de anexos e link do vídeo com correções',139,45)]:
        txt(48,y,title,10,True);field('consolidacao_'+name,48,y-height-12,499,height,True)
    txt(48,42,'Modelo em branco. Não substitui coleta e consolidação efetivas.',8,color=GRAY)
    c.save()
    return expected


if __name__=='__main__':
    create_report();fields=create_forms()
    print('PDFs gerados em',OUT)
    print('Campos preenchíveis esperados:',len(fields))

"""
MÓDULO DE EXPORTAÇÃO - Relatório PDF e Memorial Descritivo
Gera documentos técnicos formatados em PDF.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable,
)
from datetime import datetime


AZUL = HexColor("#1B3A5C")
AZUL_CLARO = HexColor("#D6E4F0")
LARANJA = HexColor("#E67E22")
CINZA = HexColor("#7F8C8D")
BRANCO = HexColor("#FFFFFF")


def _criar_estilos():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "TituloPrincipal", parent=styles["Title"],
        fontSize=18, textColor=AZUL, spaceAfter=6,
        alignment=TA_CENTER, fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        "Subtitulo", parent=styles["Heading2"],
        fontSize=13, textColor=AZUL, spaceBefore=14, spaceAfter=6,
        fontName="Helvetica-Bold", borderColor=AZUL, borderWidth=0,
        borderPadding=4,
    ))
    styles.add(ParagraphStyle(
        "Secao", parent=styles["Heading3"],
        fontSize=11, textColor=LARANJA, spaceBefore=10, spaceAfter=4,
        fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        "CorpoTexto", parent=styles["Normal"],
        fontSize=10, leading=14, alignment=TA_JUSTIFY,
        fontName="Helvetica", spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "CorpoNegrito", parent=styles["Normal"],
        fontSize=10, leading=14, fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        "Rodape", parent=styles["Normal"],
        fontSize=8, textColor=CINZA, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "Destaque", parent=styles["Normal"],
        fontSize=10, leading=14, fontName="Helvetica-Bold",
        textColor=LARANJA,
    ))
    return styles


def _tabela_estilizada(data, col_widths=None):
    """Cria tabela com estilo profissional."""
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("TEXTCOLOR", (0, 0), (-1, 0), BRANCO),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRANCO, AZUL_CLARO]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def gerar_memorial_descritivo(projeto: dict, caminho: str) -> str:
    """Gera o Memorial Descritivo de PPCI em PDF."""
    doc = SimpleDocTemplate(
        caminho, pagesize=A4,
        leftMargin=2.5 * cm, rightMargin=2.5 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    styles = _criar_estilos()
    story = []

    cls = projeto.get("classificacao", {})
    ocup = cls.get("ocupacao", {})
    risco = cls.get("risco", {})
    proc = cls.get("processo", {})
    pop = cls.get("populacao", {})
    ci = cls.get("carga_incendio", {})

    # --- CAPA ---
    story.append(Spacer(1, 3 * cm))
    story.append(Paragraph("MEMORIAL DESCRITIVO", styles["TituloPrincipal"]))
    story.append(Paragraph("PROJETO DE PREVENÇÃO E PROTEÇÃO<br/>CONTRA INCÊNDIO E PÂNICO", styles["TituloPrincipal"]))
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="60%", thickness=2, color=AZUL))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(f"<b>{projeto.get('nome_projeto', 'PROJETO PPCI')}</b>", styles["Subtitulo"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y')}", styles["CorpoTexto"]))
    story.append(Paragraph("Baseado nas Instruções Técnicas do Corpo de Bombeiros Militar da Bahia", styles["CorpoTexto"]))
    story.append(PageBreak())

    # --- 1. OBJETIVO ---
    story.append(Paragraph("1. OBJETIVO", styles["Subtitulo"]))
    story.append(Paragraph(
        "O presente Memorial Descritivo tem por objetivo descrever as medidas de segurança contra "
        "incêndio e pânico adotadas para a edificação em questão, em conformidade com as Instruções "
        "Técnicas do Corpo de Bombeiros Militar do Estado da Bahia (CBMBA) e demais normas técnicas aplicáveis.",
        styles["CorpoTexto"],
    ))

    # --- 2. DADOS DA EDIFICAÇÃO ---
    story.append(Paragraph("2. DADOS DA EDIFICAÇÃO", styles["Subtitulo"]))
    dados_tab = [
        ["Parâmetro", "Valor"],
        ["Grupo de Ocupação", f"{ocup.get('grupo', '')} — {ocup.get('nome_grupo', '')}"],
        ["Divisão", f"{ocup.get('divisao', '')} — {ocup.get('descricao', '')}"],
        ["Carga de Incêndio Adotada", f"{ci.get('adotada', 0)} MJ/m²"],
        ["Nível de Risco", risco.get("descricao", "")],
        ["População Adotada", f"{pop.get('adotada', 0)} pessoas"],
        ["Tipo de Processo", f"{proc.get('tipo', '')} — {proc.get('descricao', '')}"],
    ]
    story.append(_tabela_estilizada(dados_tab, col_widths=[6 * cm, 10 * cm]))
    story.append(Spacer(1, 0.5 * cm))

    # --- 3. CLASSIFICAÇÃO ---
    story.append(Paragraph("3. CLASSIFICAÇÃO E SISTEMAS EXIGIDOS", styles["Subtitulo"]))
    story.append(Paragraph(
        f"A edificação classifica-se no Grupo <b>{ocup.get('grupo', '')}</b> "
        f"({ocup.get('nome_grupo', '')}), Divisão <b>{ocup.get('divisao', '')}</b> "
        f"({ocup.get('descricao', '')}), com nível de risco <b>{risco.get('descricao', '')}</b>. "
        f"O tipo de processo é <b>{proc.get('tipo', '')} — {proc.get('descricao', '')}</b>. "
        f"Conforme a IT-01 do CBMBA, os seguintes sistemas de proteção são exigidos:",
        styles["CorpoTexto"],
    ))

    sistemas = cls.get("sistemas_exigidos", [])
    tab_sis = [["Cód.", "Sistema de Proteção", "IT Referência"]]
    for s in sistemas:
        tab_sis.append([s.get("codigo", ""), s.get("nome", ""), s.get("it_referencia", "")])
    story.append(_tabela_estilizada(tab_sis, col_widths=[2 * cm, 10 * cm, 4 * cm]))
    story.append(Spacer(1, 0.5 * cm))

    # --- 4. SAÍDAS DE EMERGÊNCIA ---
    saida = projeto.get("saida_emergencia", {})
    if saida:
        story.append(Paragraph("4. SAÍDAS DE EMERGÊNCIA (IT-11)", styles["Subtitulo"]))
        resumo = saida.get("resumo", {})
        story.append(Paragraph(
            f"O dimensionamento das saídas de emergência foi realizado conforme a IT-11 do CBMBA, "
            f"considerando população de <b>{resumo.get('populacao_considerada', 0)} pessoas</b>.",
            styles["CorpoTexto"],
        ))
        tab_saida = [["Parâmetro", "Valor"]]
        tab_saida.append(["Número de saídas", str(resumo.get("numero_saidas", ""))])
        tab_saida.append(["Largura adotada", f"{resumo.get('largura_adotada', '')} m ({resumo.get('unidades_passagem', '')} UP)"])
        tab_saida.append(["Distância máx. caminhamento", f"{resumo.get('distancia_maxima_caminhamento', '')} m"])
        te = resumo.get("tipo_escada")
        if te:
            tab_saida.append(["Tipo de escada", te.get("descricao", "")])
        story.append(_tabela_estilizada(tab_saida, col_widths=[6 * cm, 10 * cm]))

        for etapa in saida.get("etapas", []):
            story.append(Paragraph(
                f"<b>{etapa.get('etapa', '')}:</b> {etapa.get('formula', '')}",
                styles["CorpoTexto"],
            ))
        story.append(Spacer(1, 0.5 * cm))

    # --- 5. EXTINTORES ---
    ext = projeto.get("extintores", {})
    if ext:
        story.append(Paragraph("5. EXTINTORES DE INCÊNDIO (IT-04)", styles["Subtitulo"]))
        resumo_ext = ext.get("resumo", {})
        story.append(Paragraph(
            f"O dimensionamento dos extintores segue a IT-04 do CBMBA. "
            f"Risco classificado como <b>{resumo_ext.get('risco', '')}</b>, área máxima de proteção "
            f"por extintor de <b>{resumo_ext.get('area_maxima_protecao', '')} m²</b>, distância máxima "
            f"de caminhamento de <b>{resumo_ext.get('distancia_maxima_caminhamento', '')} m</b>.",
            styles["CorpoTexto"],
        ))
        story.append(Paragraph(
            f"Quantidade total calculada: <b>{resumo_ext.get('quantidade_total', 0)} extintores</b> "
            f"({resumo_ext.get('quantidade_por_pavimento', 0)} por pavimento).",
            styles["CorpoTexto"],
        ))
        story.append(Spacer(1, 0.5 * cm))

    # --- 6. HIDRANTES ---
    hid = projeto.get("hidrantes")
    if hid:
        story.append(Paragraph("6. SISTEMA DE HIDRANTES (IT-17)", styles["Subtitulo"]))
        rh = hid.get("resumo", {})
        story.append(Paragraph(
            f"Sistema adotado: <b>{rh.get('nome_sistema', '')}</b>. "
            f"Vazão total do sistema: <b>{rh.get('vazao_total_sistema', '')} L/min</b>. "
            f"Pressão mínima na ponta: <b>{rh.get('pressao_minima', '')} m.c.a.</b>. "
            f"Total de hidrantes: <b>{rh.get('numero_hidrantes_total', '')}</b>.",
            styles["CorpoTexto"],
        ))
        tab_hid = [["Parâmetro", "Valor"]]
        tab_hid.append(["Tipo de sistema", rh.get("nome_sistema", "")])
        tab_hid.append(["Diâmetro da mangueira", rh.get("diametro_mangueira", "")])
        tab_hid.append(["Comprimento da mangueira", f"{rh.get('comprimento_mangueira', '')} m"])
        tab_hid.append(["Tipo de esguicho", rh.get("tipo_esguicho", "")])
        tab_hid.append(["Vazão total", f"{rh.get('vazao_total_sistema', '')} L/min"])
        tab_hid.append(["Hidrantes simultâneos", str(rh.get("numero_hidrantes_simultaneos", ""))])
        tab_hid.append(["Total de hidrantes", str(rh.get("numero_hidrantes_total", ""))])
        story.append(_tabela_estilizada(tab_hid, col_widths=[6 * cm, 10 * cm]))
        story.append(Spacer(1, 0.5 * cm))

    # --- 7. RESERVA TÉCNICA ---
    res = projeto.get("reserva_tecnica")
    if res:
        story.append(Paragraph("7. RESERVA TÉCNICA DE INCÊNDIO (IT-17/IT-22)", styles["Subtitulo"]))
        rr = res.get("resumo", {})
        story.append(Paragraph(
            f"Volume adotado para a Reserva Técnica de Incêndio: "
            f"<b>{rr.get('volume_adotado_litros', '')} litros ({rr.get('volume_adotado_m3', '')} m³)</b>. "
            f"Tempo de combate considerado: <b>{rr.get('tempo_combate_minutos', '')} minutos</b>.",
            styles["CorpoTexto"],
        ))

    # --- 8. BOMBA ---
    bom = projeto.get("bomba_incendio")
    if bom:
        story.append(Paragraph("8. BOMBA DE INCÊNDIO (IT-22)", styles["Subtitulo"]))
        rb = bom.get("resumo", {})
        story.append(Paragraph(
            f"Bomba principal: <b>{rb.get('tipo_bomba', '')} — {rb.get('potencia_motor_cv', '')} CV</b>. "
            f"Vazão: <b>{rb.get('vazao_total', '')} L/min</b>. "
            f"Altura manométrica: <b>{rb.get('altura_manometrica', '')} m.c.a.</b>. "
            f"Bomba jockey: <b>{rb.get('bomba_jockey_vazao', '')} L/min a {rb.get('bomba_jockey_pressao', '')} m.c.a.</b>",
            styles["CorpoTexto"],
        ))

    # --- ENCERRAMENTO ---
    story.append(Spacer(1, 1.5 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=CINZA))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        f"Documento gerado automaticamente pelo sistema PPCI SaaS em {datetime.now().strftime('%d/%m/%Y às %H:%M')}.<br/>"
        "Baseado nas Instruções Técnicas do Corpo de Bombeiros Militar da Bahia.",
        styles["Rodape"],
    ))

    doc.build(story)
    return caminho

"""
NORMAS - Classificação de Risco de Incêndio
Baseado na IT-01 e IT-14 do CBMBA

INSTRUÇÕES PARA ATUALIZAÇÃO:
- Ajustar faixas de carga de incêndio conforme revisão das ITs
- Os valores são em MJ/m²
"""

FAIXAS_RISCO = {
    "LEVE": {
        "carga_incendio_min": 0,
        "carga_incendio_max": 300,
        "descricao": "Risco Leve (Classe A)",
        "exemplos": "Residências, escritórios, escolas, hospitais, igrejas",
        "classe_incendio_predominante": "A",
    },
    "MODERADO": {
        "carga_incendio_min": 301,
        "carga_incendio_max": 1200,
        "descricao": "Risco Moderado (Classe A e B)",
        "exemplos": "Comércio, indústria leve, marcenarias, oficinas",
        "classe_incendio_predominante": "A/B",
    },
    "ELEVADO": {
        "carga_incendio_min": 1201,
        "carga_incendio_max": 99999,
        "descricao": "Risco Elevado (Classe A, B e C)",
        "exemplos": "Refinarias, depósitos de combustíveis, fábricas de tintas",
        "classe_incendio_predominante": "A/B/C",
    },
}

CLASSES_INCENDIO = {
    "A": {
        "descricao": "Materiais sólidos combustíveis (madeira, papel, tecido, borracha, plásticos)",
        "agentes_extintores": ["Água", "Espuma", "Pó químico ABC"],
    },
    "B": {
        "descricao": "Líquidos inflamáveis e combustíveis, gases inflamáveis e graxas",
        "agentes_extintores": ["Espuma", "Pó químico BC", "Pó químico ABC", "CO2"],
    },
    "C": {
        "descricao": "Equipamentos elétricos energizados",
        "agentes_extintores": ["Pó químico BC", "Pó químico ABC", "CO2"],
    },
    "D": {
        "descricao": "Metais combustíveis (magnésio, titânio, zircônio, sódio, potássio, lítio)",
        "agentes_extintores": ["Pó químico especial"],
    },
    "K": {
        "descricao": "Óleos e gorduras em cozinhas industriais e comerciais",
        "agentes_extintores": ["Agente úmido (acetato de potássio)"],
    },
}


def classificar_risco(carga_incendio: float) -> dict:
    """Classifica o risco com base na carga de incêndio específica (MJ/m²)."""
    for nivel, faixa in FAIXAS_RISCO.items():
        if faixa["carga_incendio_min"] <= carga_incendio <= faixa["carga_incendio_max"]:
            return {
                "nivel": nivel,
                "descricao": faixa["descricao"],
                "classe_predominante": faixa["classe_incendio_predominante"],
                "carga_incendio_informada": carga_incendio,
                "norma_referencia": "IT-01 / IT-14 CBMBA",
            }
    return {
        "nivel": "INDETERMINADO",
        "descricao": "Carga de incêndio fora das faixas definidas",
        "carga_incendio_informada": carga_incendio,
    }


def obter_classe_incendio(classe: str) -> dict | None:
    """Retorna informações de uma classe de incêndio."""
    return CLASSES_INCENDIO.get(classe.upper())

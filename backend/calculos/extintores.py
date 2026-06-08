"""
MOTOR DE CÁLCULO - Extintores de Incêndio
Baseado na IT-04 do CBMBA
"""

import math
from backend.normas.tabelas_it import AREA_PROTECAO_EXTINTOR, EXTINTORES_POR_CLASSE
from backend.normas.riscos import CLASSES_INCENDIO


def calcular_extintores(dados: dict) -> dict:
    """
    Calcula a quantidade e distribuição de extintores.

    Parâmetros:
        - area_construida: float (m²)
        - risco: str (LEVE, MODERADO, ELEVADO)
        - numero_pavimentos: int
        - area_por_pavimento: float (m², se diferente entre pavimentos, usar a maior)
        - classes_incendio: list[str] (ex: ["A", "C"])
    """
    area = dados.get("area_construida", 0)
    risco = dados.get("risco", "MODERADO").upper()
    n_pav = dados.get("numero_pavimentos", 1)
    area_pav = dados.get("area_por_pavimento", area / max(n_pav, 1))
    classes = dados.get("classes_incendio", ["A", "C"])

    params = AREA_PROTECAO_EXTINTOR.get(risco, AREA_PROTECAO_EXTINTOR["MODERADO"])
    area_max = params["area_maxima"]
    dist_max = params["distancia_maxima"]

    resultados = {"etapas": [], "norma_referencia": "IT-04 CBMBA"}

    # --- 1. Quantidade por pavimento ---
    qtd_por_pavimento = max(math.ceil(area_pav / area_max), 1)
    resultados["etapas"].append({
        "etapa": "Quantidade de extintores por pavimento",
        "formula": f"N = Área_pav / Área_max = {area_pav:.0f} / {area_max} = {area_pav/area_max:.2f} → {qtd_por_pavimento}",
        "valor": qtd_por_pavimento,
        "justificativa": f"Risco {risco}: área máxima protegida = {area_max} m² por extintor",
    })

    # --- 2. Quantidade total ---
    qtd_total = qtd_por_pavimento * n_pav
    resultados["etapas"].append({
        "etapa": "Quantidade total de extintores",
        "formula": f"Total = {qtd_por_pavimento} × {n_pav} pavimentos = {qtd_total}",
        "valor": qtd_total,
    })

    # --- 3. Tipos recomendados por classe ---
    extintores_recomendados = []
    for cls in classes:
        cls_upper = cls.upper()
        opcoes = EXTINTORES_POR_CLASSE.get(cls_upper, [])
        info_classe = CLASSES_INCENDIO.get(cls_upper, {})
        extintores_recomendados.append({
            "classe": cls_upper,
            "descricao_classe": info_classe.get("descricao", ""),
            "opcoes_extintor": opcoes,
        })

    resultados["etapas"].append({
        "etapa": "Tipos de extintores recomendados",
        "formula": "Tabela IT-04 por classe de incêndio",
        "valor": [f"Classe {c}" for c in classes],
        "detalhes": extintores_recomendados,
    })

    # --- 4. Distribuição recomendada ---
    # Regra: pelo menos 1 extintor classe A e 1 classe B/C por pavimento
    distribuicao = []
    for pav in range(1, n_pav + 1):
        extintores_pav = []
        # Classe A obrigatória
        ext_a = EXTINTORES_POR_CLASSE.get("A", [{}])[0]
        extintores_pav.append({
            "tipo": ext_a.get("tipo", "Água pressurizada"),
            "capacidade": ext_a.get("capacidade", "10 L"),
            "quantidade": max(1, qtd_por_pavimento // 2),
            "classe": "A",
        })
        # Classe B/C se aplicável
        if any(c in classes for c in ["B", "C"]):
            ext_bc = EXTINTORES_POR_CLASSE.get("C", [{}])[0]
            extintores_pav.append({
                "tipo": ext_bc.get("tipo", "CO2"),
                "capacidade": ext_bc.get("capacidade", "6 kg"),
                "quantidade": max(1, qtd_por_pavimento - qtd_por_pavimento // 2),
                "classe": "B/C",
            })
        distribuicao.append({
            "pavimento": pav,
            "extintores": extintores_pav,
        })

    resultados["etapas"].append({
        "etapa": "Distribuição por pavimento",
        "formula": "Mínimo 1 extintor classe A + 1 classe BC por pavimento",
        "detalhes": distribuicao,
    })

    # --- Resumo ---
    resultados["resumo"] = {
        "risco": risco,
        "area_construida": area,
        "area_maxima_protecao": area_max,
        "distancia_maxima_caminhamento": dist_max,
        "quantidade_por_pavimento": qtd_por_pavimento,
        "quantidade_total": qtd_total,
        "classes_incendio": classes,
        "distribuicao": distribuicao,
    }

    return resultados

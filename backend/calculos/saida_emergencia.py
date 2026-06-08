"""
MOTOR DE CÁLCULO - Saídas de Emergência
Baseado na IT-11 do CBMBA

Calcula: largura de saídas, número de saídas, tipo de escada,
distância de caminhamento.
"""

import math
from backend.normas.tabelas_it import (
    CAPACIDADE_UNIDADE_PASSAGEM,
    LARGURA_MINIMA_SAIDA,
    DISTANCIA_MAXIMA_CAMINHAMENTO,
    NUMERO_MINIMO_SAIDAS,
    TIPO_ESCADA,
)


LARGURA_UNIDADE_PASSAGEM = 0.55  # metros


def calcular_saida_emergencia(dados: dict) -> dict:
    """
    Calcula o dimensionamento das saídas de emergência.

    Parâmetros:
        - populacao: int (população do pavimento mais desfavorável)
        - grupo: str (grupo de ocupação)
        - altura_edificacao: float (m)
        - numero_pavimentos: int
        - possui_subsolo: bool
        - possui_chuveiros: bool
        - area_pavimento: float (m², área do maior pavimento)
    """
    populacao = dados.get("populacao", 0)
    grupo = dados.get("grupo", "A").upper()
    altura = dados.get("altura_edificacao", 0)
    n_pav = dados.get("numero_pavimentos", 1)
    subsolo = dados.get("possui_subsolo", False)
    chuveiros = dados.get("possui_chuveiros", False)
    area_pav = dados.get("area_pavimento", 0)

    resultados = {"etapas": [], "norma_referencia": "IT-11 CBMBA"}

    # --- 1. Número mínimo de saídas ---
    n_saidas = 1
    for faixa in NUMERO_MINIMO_SAIDAS:
        if populacao <= faixa["populacao_max"]:
            n_saidas = faixa["saidas"]
            break
    resultados["etapas"].append({
        "etapa": "Número mínimo de saídas",
        "formula": "Tabela IT-11 por faixa de população",
        "valor": n_saidas,
        "unidade": "saídas",
        "justificativa": f"População de {populacao} pessoas → mínimo {n_saidas} saída(s)",
    })

    # --- 2. Largura mínima normativa ---
    largura_min_norma = LARGURA_MINIMA_SAIDA.get(grupo, 1.10)
    resultados["etapas"].append({
        "etapa": "Largura mínima normativa",
        "formula": f"Tabela IT-11 para grupo {grupo}",
        "valor": largura_min_norma,
        "unidade": "m",
    })

    # --- 3. Largura calculada por capacidade ---
    cap_acesso = CAPACIDADE_UNIDADE_PASSAGEM["ACESSO"]["capacidade"]
    cap_escada = CAPACIDADE_UNIDADE_PASSAGEM["ESCADA"]["capacidade"]

    # N = P / C (número de unidades de passagem)
    if n_pav > 1:
        capacidade_ref = cap_escada
        tipo_ref = "escada"
    else:
        capacidade_ref = cap_acesso
        tipo_ref = "acesso"

    n_unidades_passagem = math.ceil(populacao / capacidade_ref)
    if n_unidades_passagem < 2:
        n_unidades_passagem = 2  # mínimo 2 UP

    largura_calculada = n_unidades_passagem * LARGURA_UNIDADE_PASSAGEM
    largura_calculada = round(largura_calculada, 2)

    resultados["etapas"].append({
        "etapa": "Cálculo da largura por capacidade",
        "formula": f"N = P / C = {populacao} / {capacidade_ref} = {populacao/capacidade_ref:.2f} → {n_unidades_passagem} UP",
        "valor": largura_calculada,
        "unidade": "m",
        "justificativa": f"Usando capacidade de {tipo_ref}: {capacidade_ref} pessoas/UP",
    })

    # --- 4. Largura adotada (maior entre calculada e mínima) ---
    largura_adotada = max(largura_calculada, largura_min_norma)
    # Arredondar para múltiplo de 0.55
    n_up_final = math.ceil(largura_adotada / LARGURA_UNIDADE_PASSAGEM)
    largura_adotada = n_up_final * LARGURA_UNIDADE_PASSAGEM
    largura_adotada = round(largura_adotada, 2)

    resultados["etapas"].append({
        "etapa": "Largura adotada",
        "formula": f"Maior entre calculada ({largura_calculada} m) e mínima ({largura_min_norma} m), arredondada para {n_up_final} UP",
        "valor": largura_adotada,
        "unidade": "m",
    })

    # --- 5. Tipo de escada ---
    tipo_escada = None
    if n_pav > 1 or subsolo:
        for tipo, spec in TIPO_ESCADA.items():
            if altura <= spec["altura_max"]:
                tipo_escada = {
                    "tipo": tipo,
                    "descricao": spec["descricao"],
                    "aplicacao": spec["aplicacao"],
                }
                break
        resultados["etapas"].append({
            "etapa": "Tipo de escada",
            "formula": "Classificação por altura (IT-11)",
            "valor": tipo_escada["descricao"] if tipo_escada else "Não aplicável",
            "justificativa": f"Altura da edificação: {altura} m",
        })

    # --- 6. Distância máxima de caminhamento ---
    chave_chuveiro = "COM_CHUVEIROS" if chuveiros else "SEM_CHUVEIROS"
    chave_saida = "MAIS_DE_UMA_SAIDA" if n_saidas > 1 else "UNICA_SAIDA"
    dist_max = DISTANCIA_MAXIMA_CAMINHAMENTO[chave_chuveiro][chave_saida]

    resultados["etapas"].append({
        "etapa": "Distância máxima de caminhamento",
        "formula": f"Tabela IT-11 ({'com' if chuveiros else 'sem'} chuveiros, {n_saidas} saída(s))",
        "valor": dist_max,
        "unidade": "m",
    })

    # --- 7. Número de escadas ---
    n_escadas = n_saidas if n_pav > 1 else 0
    largura_escada = largura_adotada

    # --- Resumo ---
    resultados["resumo"] = {
        "populacao_considerada": populacao,
        "numero_saidas": n_saidas,
        "largura_minima_norma": largura_min_norma,
        "largura_calculada": largura_calculada,
        "largura_adotada": largura_adotada,
        "unidades_passagem": n_up_final,
        "distancia_maxima_caminhamento": dist_max,
        "tipo_escada": tipo_escada,
        "numero_escadas": n_escadas,
        "largura_escada": largura_escada,
    }

    return resultados

"""
MOTOR DE CÁLCULO - Hidrantes e Mangotinhos
Baseado na IT-17 do CBMBA
"""

import math
from backend.normas.tabelas_it import (
    TIPOS_SISTEMA_HIDRANTE,
    SISTEMA_HIDRANTE_POR_RISCO,
)


def calcular_hidrantes(dados: dict) -> dict:
    """
    Calcula o dimensionamento do sistema de hidrantes.

    Parâmetros:
        - area_construida: float (m²)
        - risco: str (LEVE, MODERADO, ELEVADO)
        - altura_edificacao: float (m)
        - numero_pavimentos: int
        - possui_subsolo: bool
    """
    area = dados.get("area_construida", 0)
    risco = dados.get("risco", "MODERADO").upper()
    altura = dados.get("altura_edificacao", 0)
    n_pav = dados.get("numero_pavimentos", 1)
    subsolo = dados.get("possui_subsolo", False)

    resultados = {"etapas": [], "norma_referencia": "IT-17 CBMBA"}

    # --- 1. Tipo de sistema ---
    tipo_key = SISTEMA_HIDRANTE_POR_RISCO.get(risco, "TIPO_2")
    sistema = TIPOS_SISTEMA_HIDRANTE[tipo_key]

    resultados["etapas"].append({
        "etapa": "Tipo de sistema de hidrantes",
        "formula": f"Tabela IT-17 para risco {risco}",
        "valor": sistema["nome"],
        "justificativa": sistema["aplicacao"],
    })

    # --- 2. Vazão e pressão mínimas ---
    vazao_min = sistema["vazao_minima_lpm"]
    pressao_min = sistema["pressao_minima_mca"]
    n_simultaneos = sistema["numero_hidrantes_simultaneos"]
    vazao_total = vazao_min * n_simultaneos

    resultados["etapas"].append({
        "etapa": "Vazão mínima por hidrante",
        "formula": f"IT-17: {vazao_min} L/min",
        "valor": vazao_min,
        "unidade": "L/min",
    })
    resultados["etapas"].append({
        "etapa": "Vazão total do sistema",
        "formula": f"Q_total = {vazao_min} × {n_simultaneos} hidrantes = {vazao_total} L/min",
        "valor": vazao_total,
        "unidade": "L/min",
    })
    resultados["etapas"].append({
        "etapa": "Pressão mínima na ponta do esguicho",
        "formula": f"IT-17: {pressao_min} m.c.a.",
        "valor": pressao_min,
        "unidade": "m.c.a.",
    })

    # --- 3. Número de hidrantes ---
    compr_mangueira = sistema["comprimento_mangueira"]
    # Raio de cobertura ≈ comprimento da mangueira + 5m (alcance do jato)
    raio_cobertura = compr_mangueira + 5
    area_coberta_por_hidrante = math.pi * (raio_cobertura ** 2)
    area_pav = area / max(n_pav, 1)

    n_hidrantes_pav = max(math.ceil(area_pav / area_coberta_por_hidrante), 1)
    n_hidrantes_total = n_hidrantes_pav * n_pav

    resultados["etapas"].append({
        "etapa": "Número de hidrantes por pavimento",
        "formula": f"Raio cobertura = {compr_mangueira} + 5 = {raio_cobertura} m → Área = π×{raio_cobertura}² = {area_coberta_por_hidrante:.0f} m² → N = {area_pav:.0f}/{area_coberta_por_hidrante:.0f}",
        "valor": n_hidrantes_pav,
        "justificativa": "Todo ponto do pavimento deve ser alcançado por pelo menos 1 hidrante",
    })
    resultados["etapas"].append({
        "etapa": "Número total de hidrantes",
        "formula": f"{n_hidrantes_pav} × {n_pav} pavimentos",
        "valor": n_hidrantes_total,
    })

    # --- 4. Especificação das mangueiras ---
    resultados["etapas"].append({
        "etapa": "Especificação da mangueira",
        "formula": "IT-17",
        "valor": f"Diâmetro: {sistema['diametro_mangueira']}, Comprimento: {compr_mangueira} m",
    })
    resultados["etapas"].append({
        "etapa": "Tipo de esguicho",
        "formula": "IT-17",
        "valor": sistema["tipo_esguicho"],
    })

    # --- Resumo ---
    resultados["resumo"] = {
        "tipo_sistema": tipo_key,
        "nome_sistema": sistema["nome"],
        "vazao_minima_hidrante": vazao_min,
        "vazao_total_sistema": vazao_total,
        "pressao_minima": pressao_min,
        "numero_hidrantes_por_pavimento": n_hidrantes_pav,
        "numero_hidrantes_total": n_hidrantes_total,
        "numero_hidrantes_simultaneos": n_simultaneos,
        "diametro_mangueira": sistema["diametro_mangueira"],
        "comprimento_mangueira": compr_mangueira,
        "tipo_esguicho": sistema["tipo_esguicho"],
    }

    return resultados

"""
MOTOR DE CÁLCULO - Reserva Técnica de Incêndio (RTI)
Baseado na IT-17 e IT-22 do CBMBA
"""

import math
from backend.normas.tabelas_it import (
    TIPOS_SISTEMA_HIDRANTE,
    SISTEMA_HIDRANTE_POR_RISCO,
    TEMPO_COMBATE,
    VOLUME_MINIMO_RESERVA,
    EFICIENCIA_BOMBA,
    FATOR_SEGURANCA_BOMBA,
)


def calcular_reserva_tecnica(dados: dict) -> dict:
    """
    Calcula o volume da Reserva Técnica de Incêndio.

    Parâmetros:
        - risco: str
        - vazao_total_sistema: float (L/min) — obtida do cálculo de hidrantes
        - possui_chuveiros: bool
        - vazao_chuveiros: float (L/min, se aplicável)
    """
    risco = dados.get("risco", "MODERADO").upper()
    possui_chuveiros = dados.get("possui_chuveiros", False)
    vazao_chuveiros = dados.get("vazao_chuveiros", 0)

    tipo_key = SISTEMA_HIDRANTE_POR_RISCO.get(risco, "TIPO_2")
    sistema = TIPOS_SISTEMA_HIDRANTE[tipo_key]
    vazao_hidrantes = sistema["vazao_minima_lpm"] * sistema["numero_hidrantes_simultaneos"]
    vazao_fornecida = dados.get("vazao_total_sistema", vazao_hidrantes)

    tempo = TEMPO_COMBATE.get(tipo_key, 60)
    vol_minimo_norma = VOLUME_MINIMO_RESERVA.get(tipo_key, 8000)

    resultados = {"etapas": [], "norma_referencia": "IT-17 / IT-22 CBMBA"}

    # --- 1. Volume para hidrantes ---
    vol_hidrantes = vazao_fornecida * tempo  # litros
    resultados["etapas"].append({
        "etapa": "Volume para sistema de hidrantes",
        "formula": f"V = Q × t = {vazao_fornecida} L/min × {tempo} min = {vol_hidrantes} L",
        "valor": vol_hidrantes,
        "unidade": "litros",
    })

    # --- 2. Volume para chuveiros (se aplicável) ---
    vol_chuveiros = 0
    if possui_chuveiros and vazao_chuveiros > 0:
        tempo_chuveiros = 60  # minutos padrão
        vol_chuveiros = vazao_chuveiros * tempo_chuveiros
        resultados["etapas"].append({
            "etapa": "Volume para chuveiros automáticos",
            "formula": f"V = {vazao_chuveiros} L/min × {tempo_chuveiros} min = {vol_chuveiros} L",
            "valor": vol_chuveiros,
            "unidade": "litros",
        })

    # --- 3. Volume total calculado ---
    vol_total_calc = vol_hidrantes + vol_chuveiros
    resultados["etapas"].append({
        "etapa": "Volume total calculado",
        "formula": f"V_total = {vol_hidrantes} + {vol_chuveiros} = {vol_total_calc} L",
        "valor": vol_total_calc,
        "unidade": "litros",
    })

    # --- 4. Volume adotado (maior entre calculado e mínimo normativo) ---
    vol_adotado = max(vol_total_calc, vol_minimo_norma)
    vol_adotado_m3 = vol_adotado / 1000

    resultados["etapas"].append({
        "etapa": "Volume adotado",
        "formula": f"Maior entre calculado ({vol_total_calc} L) e mínimo normativo ({vol_minimo_norma} L)",
        "valor": vol_adotado,
        "unidade": "litros",
        "valor_m3": vol_adotado_m3,
    })

    resultados["resumo"] = {
        "tipo_sistema": tipo_key,
        "vazao_hidrantes": vazao_fornecida,
        "vazao_chuveiros": vazao_chuveiros,
        "tempo_combate_minutos": tempo,
        "volume_hidrantes": vol_hidrantes,
        "volume_chuveiros": vol_chuveiros,
        "volume_calculado": vol_total_calc,
        "volume_minimo_norma": vol_minimo_norma,
        "volume_adotado_litros": vol_adotado,
        "volume_adotado_m3": vol_adotado_m3,
    }

    return resultados


def calcular_bomba_incendio(dados: dict) -> dict:
    """
    Calcula a potência da bomba de incêndio.

    Parâmetros:
        - vazao_total: float (L/min)
        - pressao_necessaria: float (m.c.a.)
        - altura_edificacao: float (m)
        - pressao_minima_ponta: float (m.c.a.)
        - perda_carga_estimada: float (m.c.a., estimativa)
    """
    vazao = dados.get("vazao_total", 300)  # L/min
    altura = dados.get("altura_edificacao", 12)
    pressao_ponta = dados.get("pressao_minima_ponta", 15)
    perda_carga = dados.get("perda_carga_estimada", 5)

    resultados = {"etapas": [], "norma_referencia": "IT-22 CBMBA"}

    # --- 1. Altura manométrica total ---
    hm_total = altura + pressao_ponta + perda_carga
    resultados["etapas"].append({
        "etapa": "Altura manométrica total",
        "formula": f"Hm = Altura({altura}) + Pressão_ponta({pressao_ponta}) + Perda_carga({perda_carga}) = {hm_total} m.c.a.",
        "valor": hm_total,
        "unidade": "m.c.a.",
    })

    # --- 2. Vazão em m³/s ---
    vazao_m3s = vazao / 60000
    resultados["etapas"].append({
        "etapa": "Vazão em m³/s",
        "formula": f"Q = {vazao} / 60000 = {vazao_m3s:.6f} m³/s",
        "valor": round(vazao_m3s, 6),
        "unidade": "m³/s",
    })

    # --- 3. Potência hidráulica ---
    # P = (ρ × g × Q × Hm) / η
    rho = 1000  # kg/m³
    g = 9.81    # m/s²
    pot_hidraulica_w = (rho * g * vazao_m3s * hm_total)
    pot_hidraulica_cv = pot_hidraulica_w / 735.5

    resultados["etapas"].append({
        "etapa": "Potência hidráulica",
        "formula": f"P = ρ×g×Q×Hm = {rho}×{g}×{vazao_m3s:.6f}×{hm_total} = {pot_hidraulica_w:.1f} W ({pot_hidraulica_cv:.2f} CV)",
        "valor": round(pot_hidraulica_cv, 2),
        "unidade": "CV",
    })

    # --- 4. Potência de eixo (com rendimento) ---
    pot_eixo = pot_hidraulica_cv / EFICIENCIA_BOMBA
    resultados["etapas"].append({
        "etapa": "Potência de eixo (rendimento η = 65%)",
        "formula": f"P_eixo = {pot_hidraulica_cv:.2f} / {EFICIENCIA_BOMBA} = {pot_eixo:.2f} CV",
        "valor": round(pot_eixo, 2),
        "unidade": "CV",
    })

    # --- 5. Potência do motor (com fator de segurança) ---
    pot_motor = pot_eixo * FATOR_SEGURANCA_BOMBA
    # Arredondar para CV comercial mais próximo
    cvs_comerciais = [0.5, 0.75, 1, 1.5, 2, 3, 5, 7.5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 100, 125, 150]
    pot_comercial = pot_motor
    for cv in cvs_comerciais:
        if cv >= pot_motor:
            pot_comercial = cv
            break

    resultados["etapas"].append({
        "etapa": "Potência do motor (fator segurança 1,25)",
        "formula": f"P_motor = {pot_eixo:.2f} × {FATOR_SEGURANCA_BOMBA} = {pot_motor:.2f} CV → Comercial: {pot_comercial} CV",
        "valor": pot_comercial,
        "unidade": "CV",
    })

    # --- 6. Bomba jockey ---
    vazao_jockey = vazao * 0.10  # 10% da vazão principal
    pressao_jockey = hm_total * 1.15  # 15% acima da principal

    resultados["etapas"].append({
        "etapa": "Bomba jockey (pressurização)",
        "formula": f"Q_jockey = 10% × {vazao} = {vazao_jockey:.0f} L/min | P_jockey = 1,15 × {hm_total} = {pressao_jockey:.1f} m.c.a.",
        "valor": f"{vazao_jockey:.0f} L/min a {pressao_jockey:.1f} m.c.a.",
    })

    resultados["resumo"] = {
        "vazao_total": vazao,
        "altura_manometrica": hm_total,
        "potencia_hidraulica_cv": round(pot_hidraulica_cv, 2),
        "potencia_eixo_cv": round(pot_eixo, 2),
        "potencia_motor_cv": pot_comercial,
        "tipo_bomba": "Centrífuga",
        "bomba_jockey_vazao": round(vazao_jockey, 1),
        "bomba_jockey_pressao": round(pressao_jockey, 1),
        "eficiencia": EFICIENCIA_BOMBA,
        "fator_seguranca": FATOR_SEGURANCA_BOMBA,
    }

    return resultados

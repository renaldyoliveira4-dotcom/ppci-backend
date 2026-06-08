"""
MOTOR DE CLASSIFICAÇÃO
Identifica ocupação, risco, tipo de processo e sistemas exigidos.
"""

from backend.normas.ocupacoes import obter_ocupacao
from backend.normas.riscos import classificar_risco
from backend.normas.sistemas_exigidos import (
    determinar_sistemas_exigidos,
    definir_tipo_processo,
)


def classificar_edificacao(dados: dict) -> dict:
    """
    Motor principal de classificação da edificação.
    
    Parâmetros esperados em 'dados':
        - grupo: str (ex: "D")
        - divisao: str (ex: "D-1")
        - area_construida: float
        - altura_edificacao: float
        - carga_incendio: float (MJ/m²)
        - possui_subsolo: bool
        - populacao: int (opcional, será calculado se não informado)
    
    Retorna dict com classificação completa.
    """
    grupo = dados.get("grupo", "")
    divisao = dados.get("divisao", "")
    area = dados.get("area_construida", 0)
    altura = dados.get("altura_edificacao", 0)
    carga = dados.get("carga_incendio", 0)
    subsolo = dados.get("possui_subsolo", False)
    populacao_informada = dados.get("populacao")

    # 1. Identificar ocupação
    ocupacao = obter_ocupacao(grupo, divisao)
    if not ocupacao:
        return {"erro": f"Ocupação {grupo}/{divisao} não encontrada na base normativa."}

    # 2. Calcular população se não informada
    if not populacao_informada:
        populacao_calculada = int(area * ocupacao["populacao_por_m2"])
    else:
        populacao_calculada = populacao_informada

    # 3. Definir carga de incêndio (usar da norma se não informada)
    if not carga or carga <= 0:
        carga = ocupacao.get("carga_incendio_especifica", 300)

    # 4. Classificar risco
    risco = classificar_risco(carga)

    # 5. Definir tipo de processo (PTS ou Projeto Técnico)
    processo = definir_tipo_processo(area, altura, grupo, divisao)

    # 6. Determinar sistemas exigidos
    sistemas = determinar_sistemas_exigidos(
        area_construida=area,
        altura=altura,
        grupo=grupo,
        risco=risco["nivel"],
        possui_subsolo=subsolo,
    )

    return {
        "ocupacao": {
            "grupo": ocupacao["grupo"],
            "nome_grupo": ocupacao["nome_grupo"],
            "divisao": ocupacao["divisao"],
            "descricao": ocupacao["descricao"],
            "exemplos": ocupacao["exemplos"],
        },
        "populacao": {
            "informada": populacao_informada,
            "calculada": populacao_calculada,
            "fator_usado": ocupacao["populacao_por_m2"],
            "adotada": populacao_informada or populacao_calculada,
        },
        "carga_incendio": {
            "informada": dados.get("carga_incendio", 0),
            "norma": ocupacao.get("carga_incendio_especifica", 0),
            "adotada": carga,
        },
        "risco": risco,
        "processo": processo,
        "sistemas_exigidos": sistemas,
        "total_sistemas": len(sistemas),
        "norma_referencia": "IT-01 CBMBA",
    }

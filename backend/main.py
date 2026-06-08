"""
PPCI SaaS - Backend FastAPI
Servidor principal com endpoints para classificação, cálculos e exportações.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List

from backend.calculos.classificacao import classificar_edificacao
from backend.calculos.saida_emergencia import calcular_saida_emergencia
from backend.calculos.extintores import calcular_extintores
from backend.calculos.hidrantes import calcular_hidrantes
from backend.calculos.reserva_bomba import calcular_reserva_tecnica, calcular_bomba_incendio
from backend.normas.ocupacoes import listar_grupos, listar_divisoes
from backend.ai.plant_analysis import analisar_planta

app = FastAPI(
    title="PPCI SaaS API",
    description="API para dimensionamento de projetos de Prevenção e Proteção Contra Incêndio — CBMBA",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SCHEMAS
# ============================================================

class EdificacaoInput(BaseModel):
    grupo: str = Field(..., description="Grupo de ocupação (A-J)")
    divisao: str = Field(..., description="Divisão (ex: D-1)")
    area_construida: float = Field(..., gt=0)
    altura_edificacao: float = Field(0, ge=0)
    numero_pavimentos: int = Field(1, ge=1)
    carga_incendio: Optional[float] = Field(None, ge=0, description="MJ/m²")
    populacao: Optional[int] = Field(None, ge=0)
    possui_subsolo: bool = False
    numero_subsolos: int = Field(0, ge=0)


class SaidaEmergenciaInput(BaseModel):
    populacao: int = Field(..., gt=0)
    grupo: str
    altura_edificacao: float = Field(0, ge=0)
    numero_pavimentos: int = Field(1, ge=1)
    possui_subsolo: bool = False
    possui_chuveiros: bool = False
    area_pavimento: float = Field(0, ge=0)


class ExtintoresInput(BaseModel):
    area_construida: float = Field(..., gt=0)
    risco: str = Field("MODERADO", description="LEVE, MODERADO ou ELEVADO")
    numero_pavimentos: int = Field(1, ge=1)
    area_por_pavimento: Optional[float] = None
    classes_incendio: list[str] = Field(default=["A", "C"])


class HidrantesInput(BaseModel):
    area_construida: float = Field(..., gt=0)
    risco: str = Field("MODERADO")
    altura_edificacao: float = Field(0, ge=0)
    numero_pavimentos: int = Field(1, ge=1)
    possui_subsolo: bool = False


class ReservaTecnicaInput(BaseModel):
    risco: str = Field("MODERADO")
    vazao_total_sistema: Optional[float] = None
    possui_chuveiros: bool = False
    vazao_chuveiros: float = Field(0, ge=0)


class BombaIncendioInput(BaseModel):
    vazao_total: float = Field(..., gt=0, description="L/min")
    altura_edificacao: float = Field(..., ge=0)
    pressao_minima_ponta: float = Field(15, ge=0, description="m.c.a.")
    perda_carga_estimada: float = Field(5, ge=0, description="m.c.a.")


class ProjetoCompletoInput(BaseModel):
    """Entrada para cálculo completo de um projeto."""
    nome_projeto: str
    grupo: str
    divisao: str
    area_construida: float = Field(..., gt=0)
    altura_edificacao: float = Field(0, ge=0)
    numero_pavimentos: int = Field(1, ge=1)
    carga_incendio: Optional[float] = None
    populacao: Optional[int] = None
    possui_subsolo: bool = False
    numero_subsolos: int = 0
    possui_chuveiros: bool = False


# ============================================================
# ENDPOINTS - NORMAS
# ============================================================

@app.get("/api/normas/grupos")
def api_listar_grupos():
    """Lista todos os grupos de ocupação disponíveis."""
    return {"grupos": listar_grupos()}


@app.get("/api/normas/divisoes/{grupo}")
def api_listar_divisoes(grupo: str):
    """Lista divisões de um grupo de ocupação."""
    divisoes = listar_divisoes(grupo)
    if not divisoes:
        raise HTTPException(404, f"Grupo '{grupo}' não encontrado")
    return {"grupo": grupo, "divisoes": divisoes}


# ============================================================
# ENDPOINTS - CÁLCULOS INDIVIDUAIS
# ============================================================

@app.post("/api/calculos/classificacao")
def api_classificar(dados: EdificacaoInput):
    """Classifica a edificação: ocupação, risco, processo e sistemas."""
    resultado = classificar_edificacao(dados.model_dump())
    if "erro" in resultado:
        raise HTTPException(400, resultado["erro"])
    return resultado


@app.post("/api/calculos/saida-emergencia")
def api_saida_emergencia(dados: SaidaEmergenciaInput):
    """Calcula dimensionamento das saídas de emergência."""
    return calcular_saida_emergencia(dados.model_dump())


@app.post("/api/calculos/extintores")
def api_extintores(dados: ExtintoresInput):
    """Calcula quantidade e distribuição de extintores."""
    return calcular_extintores(dados.model_dump())


@app.post("/api/calculos/hidrantes")
def api_hidrantes(dados: HidrantesInput):
    """Calcula dimensionamento do sistema de hidrantes."""
    return calcular_hidrantes(dados.model_dump())


@app.post("/api/calculos/reserva-tecnica")
def api_reserva_tecnica(dados: ReservaTecnicaInput):
    """Calcula volume da Reserva Técnica de Incêndio."""
    return calcular_reserva_tecnica(dados.model_dump())


@app.post("/api/calculos/bomba-incendio")
def api_bomba_incendio(dados: BombaIncendioInput):
    """Calcula potência da bomba de incêndio."""
    return calcular_bomba_incendio(dados.model_dump())


# ============================================================
# ENDPOINT - CÁLCULO COMPLETO DO PROJETO
# ============================================================

@app.post("/api/calculos/projeto-completo")
def api_projeto_completo(dados: ProjetoCompletoInput):
    """
    Executa TODOS os cálculos de um projeto de uma vez.
    Retorna classificação + todos os dimensionamentos.
    """
    d = dados.model_dump()

    # 1. Classificação
    classificacao = classificar_edificacao({
        "grupo": d["grupo"],
        "divisao": d["divisao"],
        "area_construida": d["area_construida"],
        "altura_edificacao": d["altura_edificacao"],
        "carga_incendio": d.get("carga_incendio", 0),
        "possui_subsolo": d["possui_subsolo"],
        "populacao": d.get("populacao"),
    })
    if "erro" in classificacao:
        raise HTTPException(400, classificacao["erro"])

    populacao_adotada = classificacao["populacao"]["adotada"]
    risco = classificacao["risco"]["nivel"]
    area_pav = d["area_construida"] / max(d["numero_pavimentos"], 1)

    # 2. Saída de emergência
    saida = calcular_saida_emergencia({
        "populacao": populacao_adotada,
        "grupo": d["grupo"],
        "altura_edificacao": d["altura_edificacao"],
        "numero_pavimentos": d["numero_pavimentos"],
        "possui_subsolo": d["possui_subsolo"],
        "possui_chuveiros": d.get("possui_chuveiros", False),
        "area_pavimento": area_pav,
    })

    # 3. Extintores
    extintores = calcular_extintores({
        "area_construida": d["area_construida"],
        "risco": risco,
        "numero_pavimentos": d["numero_pavimentos"],
        "area_por_pavimento": area_pav,
        "classes_incendio": ["A", "C"],
    })

    # 4. Hidrantes (se exigido)
    hidrantes = None
    sistemas_ids = [s["id"] for s in classificacao["sistemas_exigidos"]]
    if "HIDRANTES" in sistemas_ids:
        hidrantes = calcular_hidrantes({
            "area_construida": d["area_construida"],
            "risco": risco,
            "altura_edificacao": d["altura_edificacao"],
            "numero_pavimentos": d["numero_pavimentos"],
            "possui_subsolo": d["possui_subsolo"],
        })

    # 5. Reserva Técnica (se hidrantes exigidos)
    reserva = None
    if hidrantes:
        vazao_hid = hidrantes["resumo"]["vazao_total_sistema"]
        reserva = calcular_reserva_tecnica({
            "risco": risco,
            "vazao_total_sistema": vazao_hid,
            "possui_chuveiros": d.get("possui_chuveiros", False),
        })

    # 6. Bomba de Incêndio (se hidrantes exigidos)
    bomba = None
    if hidrantes:
        bomba = calcular_bomba_incendio({
            "vazao_total": hidrantes["resumo"]["vazao_total_sistema"],
            "altura_edificacao": d["altura_edificacao"],
            "pressao_minima_ponta": hidrantes["resumo"]["pressao_minima"],
            "perda_carga_estimada": 5,
        })

    return {
        "nome_projeto": d["nome_projeto"],
        "classificacao": classificacao,
        "saida_emergencia": saida,
        "extintores": extintores,
        "hidrantes": hidrantes,
        "reserva_tecnica": reserva,
        "bomba_incendio": bomba,
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "PPCI SaaS API", "version": "1.0.0"}


# ============================================================
# ENDPOINT - ANÁLISE DE PLANTA COM IA (Anthropic Claude)
# ============================================================

@app.post("/api/ai/analyze-plant")
async def api_analyze_plant(
    file: UploadFile = File(...),
    files: List[UploadFile] = File(None),
    memorial: Optional[UploadFile] = File(None),
    instrucoes: Optional[str] = Form(None),
):
    """
    Audita um conjunto de plantas de combate a incêndio (planta baixa, cortes,
    cobertura, etc.) e o memorial, se enviado, usando IA real.

    Aceita várias plantas em "files" (PDF até 32MB; PNG/JPG/WEBP até 20MB cada).
    CAD (DWG/DXF/RVT/IFC): retorna mensagem solicitando conversão para PDF.

    Requer variável de ambiente ANTHROPIC_API_KEY configurada no servidor.
    """
    if not file.filename:
        raise HTTPException(400, "Nenhum arquivo enviado")

    # Junta todas as plantas: "file" (compat.) + "files" (múltiplas), sem duplicar.
    plantas = []
    vistos = set()
    candidatos = [file] + (files or [])
    for uf in candidatos:
        if uf is None or not getattr(uf, "filename", None):
            continue
        dados = await uf.read()
        if not dados:
            continue
        chave = (uf.filename, len(dados))
        if chave in vistos:
            continue
        vistos.add(chave)
        plantas.append({
            "bytes": dados,
            "filename": uf.filename,
            "content_type": uf.content_type,
        })

    if not plantas:
        raise HTTPException(400, "Arquivo vazio")

    memorial_bytes = None
    memorial_filename = None
    memorial_content_type = None
    if memorial is not None and memorial.filename:
        memorial_bytes = await memorial.read()
        memorial_filename = memorial.filename
        memorial_content_type = memorial.content_type

    resultado = analisar_planta(
        plantas=plantas,
        instrucoes_extras=instrucoes,
        memorial_bytes=memorial_bytes,
        memorial_filename=memorial_filename,
        memorial_content_type=memorial_content_type,
    )
    return resultado


@app.get("/api/ai/status")
def api_ai_status():
    """Verifica se a IA está configurada e disponível."""
    api_key_set = bool(os.environ.get("ANTHROPIC_API_KEY"))
    try:
        from anthropic import Anthropic  # noqa
        sdk_installed = True
    except ImportError:
        sdk_installed = False
    return {
        "ai_enabled": api_key_set and sdk_installed,
        "api_key_configured": api_key_set,
        "sdk_installed": sdk_installed,
        "model_default": "claude-sonnet-4-6",
    }


# ============================================================
# INICIALIZAÇÃO DO SERVIDOR (lê PORT do ambiente)
# ============================================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port)

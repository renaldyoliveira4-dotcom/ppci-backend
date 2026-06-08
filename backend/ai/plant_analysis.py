"""
Serviço de análise de plantas com IA real (Anthropic Claude API).

Suporta:
- PDF nativo (até 32MB, 100 páginas) → Claude lê diretamente
- Imagens PNG/JPG/JPEG → Claude vision
- CAD (DWG/DXF/RVT/IFC) → não suportado nativamente; retorna mensagem clara

Requer variável de ambiente: ANTHROPIC_API_KEY
"""

import os
import base64
import json
import re
from typing import Optional

try:
    from anthropic import Anthropic, APIError
except ImportError:
    Anthropic = None
    APIError = Exception

from backend.ai.prompts import SYSTEM_PROMPT_PPCI


# Modelo recomendado para análise de plantas (boa visão + custo razoável)
# Sonnet 4.6 é o equilíbrio ideal entre capacidade e preço
MODEL_DEFAULT = "claude-sonnet-4-6"

MAX_TOKENS = 6000
PDF_MAX_BYTES = 32 * 1024 * 1024  # 32 MB
IMG_MAX_BYTES = 20 * 1024 * 1024  # 20 MB

SUPPORTED_PDF = {"application/pdf"}
SUPPORTED_IMG = {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"}
UNSUPPORTED_CAD = {".dwg", ".dxf", ".rvt", ".ifc"}


def _classificar_arquivo(filename: str, content_type: Optional[str] = None) -> dict:
    """Classifica o tipo de arquivo e seu método de processamento."""
    name = filename.lower()
    ext = "." + name.split(".")[-1] if "." in name else ""

    if ext == ".pdf" or content_type == "application/pdf":
        return {"tipo": "pdf", "media_type": "application/pdf"}
    if ext in {".png"} or content_type == "image/png":
        return {"tipo": "imagem", "media_type": "image/png"}
    if ext in {".jpg", ".jpeg"} or content_type in {"image/jpeg", "image/jpg"}:
        return {"tipo": "imagem", "media_type": "image/jpeg"}
    if ext == ".webp" or content_type == "image/webp":
        return {"tipo": "imagem", "media_type": "image/webp"}
    if ext in UNSUPPORTED_CAD:
        return {"tipo": "cad", "media_type": None}
    return {"tipo": "desconhecido", "media_type": None}


def _resposta_fallback_cad(filename: str) -> dict:
    """Resposta para arquivos CAD que o Claude não consegue ler nativamente."""
    ext = filename.split(".")[-1].upper() if "." in filename else "?"
    return {
        "confianca_geral": "pendente",
        "encontrados": [],
        "sistemas_identificados": [],
        "pendencias": [
            f"O arquivo {filename} (.{ext}) é um formato CAD/BIM que não pode ser lido diretamente pela IA.",
            "Para análise automática, exporte uma versão em PDF da planta com as pranchas técnicas.",
            "Recomendado: pranchas com quadro de áreas, cortes, plantas baixas dos pavimentos e legenda.",
        ],
        "inconsistencias": [
            {
                "tipo": "info",
                "texto": f"Para projetos {ext}, recomenda-se também fazer upload de PDF gerado a partir do mesmo arquivo, com as pranchas técnicas. A leitura nativa de {ext} requer integração BIM futura (plugin Revit / ifcopenshell).",
            }
        ],
        "sugestao_enquadramento": {
            "grupo": "",
            "divisao": "",
            "descricao": "Aguardando análise — envie PDF com pranchas técnicas",
            "risco": "PENDENTE",
            "processo": "Pendente",
            "justificativa": "Não foi possível analisar o arquivo CAD diretamente. Envie um PDF.",
            "its_aplicaveis": [],
        },
    }


def _resposta_erro(mensagem: str) -> dict:
    """Resposta padronizada para erros."""
    return {
        "confianca_geral": "baixa",
        "erro": mensagem,
        "encontrados": [],
        "sistemas_identificados": [],
        "pendencias": [mensagem, "Tente novamente ou contate o suporte."],
        "inconsistencias": [],
        "sugestao_enquadramento": {
            "grupo": "", "divisao": "", "descricao": "Erro na análise",
            "risco": "PENDENTE", "processo": "Erro", "justificativa": mensagem,
            "its_aplicaveis": [],
        },
    }


def _extrair_json(texto: str) -> Optional[dict]:
    """
    Extrai JSON do texto retornado pelo Claude, tolerando:
    - Markdown ```json ... ```
    - Markdown ``` ... ```
    - Texto antes/depois do JSON
    - Espaços/quebras de linha extras
    - JSON aninhado com {} dentro
    """
    if not texto:
        return None

    # Estratégia 1: Tenta extrair conteúdo entre fences markdown
    # Procura por ```json ... ``` ou ``` ... ```
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", texto, re.DOTALL | re.IGNORECASE)
    if fence_match:
        candidato = fence_match.group(1).strip()
        try:
            return json.loads(candidato)
        except json.JSONDecodeError:
            pass

    # Estratégia 2: Remove todos os marcadores de fence e tenta parsear
    limpo = texto
    limpo = re.sub(r"```(?:json)?\s*\n?", "", limpo, flags=re.IGNORECASE)
    limpo = re.sub(r"\n?```\s*", "", limpo)
    limpo = limpo.strip()
    try:
        return json.loads(limpo)
    except json.JSONDecodeError:
        pass

    # Estratégia 3: Encontra o primeiro { e tenta achar o } correspondente,
    # contando profundidade para lidar com objetos aninhados
    start = limpo.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False
    end = -1
    for i in range(start, len(limpo)):
        c = limpo[i]
        if escape:
            escape = False
            continue
        if c == "\\":
            escape = True
            continue
        if c == '"' and not escape:
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i
                break

    if end == -1:
        return None

    candidato = limpo[start:end + 1]
    try:
        return json.loads(candidato)
    except json.JSONDecodeError:
        return None


def _bloco_conteudo(arquivo_bytes: bytes, filename: str, content_type, rotulo: str):
    """Monta um content block (document/image) para um arquivo, validando tipo e tamanho.
    Retorna (lista_de_blocos, erro) — erro é None se ok."""
    classificacao = _classificar_arquivo(filename, content_type)
    tipo = classificacao["tipo"]
    if tipo == "cad":
        return None, f"O {rotulo} ({filename}) é um arquivo CAD/BIM. Exporte em PDF."
    if tipo == "desconhecido":
        return None, f"Tipo de arquivo não suportado no {rotulo}: {filename}. Aceitos: PDF, PNG, JPG, WEBP."
    tamanho = len(arquivo_bytes)
    if tipo == "pdf" and tamanho > PDF_MAX_BYTES:
        return None, f"{rotulo} PDF muito grande ({tamanho/1024/1024:.1f} MB). Máx: {PDF_MAX_BYTES/1024/1024:.0f} MB."
    if tipo == "imagem" and tamanho > IMG_MAX_BYTES:
        return None, f"{rotulo} (imagem) muito grande ({tamanho/1024/1024:.1f} MB). Máx: {IMG_MAX_BYTES/1024/1024:.0f} MB."
    b64 = base64.standard_b64encode(arquivo_bytes).decode("utf-8")
    media_type = classificacao["media_type"]
    rotulo_block = {"type": "text", "text": f"--- {rotulo.upper()}: {filename} ---"}
    if tipo == "pdf":
        file_block = {"type": "document", "source": {"type": "base64", "media_type": media_type, "data": b64}}
    else:
        file_block = {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}}
    return [rotulo_block, file_block], None


def analisar_planta(
    plantas: Optional[list] = None,
    arquivo_bytes: Optional[bytes] = None,
    filename: Optional[str] = None,
    content_type: Optional[str] = None,
    instrucoes_extras: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = MODEL_DEFAULT,
    memorial_bytes: Optional[bytes] = None,
    memorial_filename: Optional[str] = None,
    memorial_content_type: Optional[str] = None,
) -> dict:
    """
    Audita um CONJUNTO de plantas PPCI (planta baixa, cortes, cobertura, etc.)
    usando IA real da Anthropic.

    Args:
        plantas: lista de dicts {bytes, filename, content_type} — várias pranchas.
        arquivo_bytes/filename/content_type: forma antiga (1 arquivo); ainda aceita.
        memorial_*: memorial descritivo opcional.

    Returns:
        dict com estrutura compatível com o frontend
    """
    if Anthropic is None:
        return _resposta_erro(
            "Biblioteca anthropic não instalada. Execute: pip install anthropic"
        )

    # Normaliza a entrada para uma lista de plantas
    if not plantas:
        if arquivo_bytes and filename:
            plantas = [{"bytes": arquivo_bytes, "filename": filename, "content_type": content_type}]
        else:
            return _resposta_erro("Nenhuma planta enviada.")

    # CAD/BIM: se a PRIMEIRA planta for CAD, orienta conversão
    primeira = plantas[0]
    classif0 = _classificar_arquivo(primeira["filename"], primeira.get("content_type"))
    if classif0["tipo"] == "cad":
        return _resposta_fallback_cad(primeira["filename"])

    # A partir daqui precisa de API key
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _resposta_erro(
            "Chave da API Anthropic não configurada. Defina ANTHROPIC_API_KEY."
        )

    # Monta os blocos: TODAS as plantas + memorial (opcional)
    content = []
    nomes_plantas = []
    for i, pl in enumerate(plantas, start=1):
        rotulo = f"planta {i}/{len(plantas)} — {pl['filename']}"
        blocos, erro = _bloco_conteudo(pl["bytes"], pl["filename"], pl.get("content_type"), rotulo)
        if erro:
            # Pula um arquivo problemático em vez de falhar tudo, mas registra
            content.append({"type": "text", "text": f"[AVISO] {erro}"})
            continue
        content += blocos
        nomes_plantas.append(pl["filename"])

    if not nomes_plantas:
        return _resposta_erro("Nenhuma das plantas pôde ser lida (verifique o formato: PDF, PNG, JPG).")

    tem_memorial = bool(memorial_bytes) and bool(memorial_filename)
    if tem_memorial:
        blocos_mem, erro_mem = _bloco_conteudo(
            memorial_bytes, memorial_filename, memorial_content_type, "memorial descritivo"
        )
        if erro_mem:
            return _resposta_erro(erro_mem)
        content += blocos_mem

    instrucao_usuario = (
        f"Foram enviadas {len(nomes_plantas)} prancha(s) do MESMO projeto de combate a incêndio "
        f"({', '.join(nomes_plantas)})"
        + (" mais o memorial descritivo" if tem_memorial else "")
        + ". Elas se COMPLEMENTAM: a planta baixa mostra a distribuição dos sistemas em planta, "
        "os cortes mostram alturas e prumadas, e a cobertura mostra o nível superior. "
        "ANALISE TODAS EM CONJUNTO como um único projeto — NÃO trate uma prancha isolada nem "
        "afirme que falta a planta baixa se houver uma prancha de planta entre os arquivos enviados. "
        "Antes de dizer que um sistema está ausente, verifique em TODAS as pranchas. "
        "Faça a auditoria de conformidade conforme as ITs do CBMBA: enquadramento correto?, "
        "audite cada sistema exigido (conforme / não conforme / pendente), aponte divergências "
        "e atribua a NOTA (0 a 10) e o STATUS. Responda APENAS com o JSON do system prompt."
    )
    if instrucoes_extras:
        instrucao_usuario += f"\n\nInstruções adicionais do usuário: {instrucoes_extras}"
    content.append({"type": "text", "text": instrucao_usuario})

    try:
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT_PPCI,
            messages=[{"role": "user", "content": content}],
        )
    except APIError as e:
        return _resposta_erro(f"Erro da API Anthropic: {str(e)}")
    except Exception as e:
        return _resposta_erro(f"Erro inesperado: {type(e).__name__}: {str(e)}")

    # Extrai o texto da resposta
    texto_resposta = ""
    for block in response.content:
        if hasattr(block, "text"):
            texto_resposta += block.text

    # Tenta parsear JSON
    resultado = _extrair_json(texto_resposta)
    if not resultado:
        return _resposta_erro(
            f"IA retornou resposta não-JSON. Trecho: {texto_resposta[:200]}..."
        )

    # Adiciona metadados úteis
    resultado["_meta"] = {
        "model": model,
        "input_tokens": getattr(response.usage, "input_tokens", None),
        "output_tokens": getattr(response.usage, "output_tokens", None),
        "arquivos": nomes_plantas,
        "memorial": memorial_filename if tem_memorial else None,
    }

    return resultado

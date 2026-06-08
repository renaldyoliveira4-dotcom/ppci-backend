"""
Vercel Serverless Function — Análise de planta PPCI com IA
Endpoint: POST /api/analyze-plant
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import base64
import cgi
import io

def analisar_com_ia(plantas, memorial_bytes=None, memorial_filename=None, memorial_content_type=None, instrucoes=None):
    try:
        import anthropic
    except ImportError:
        return {"erro": "anthropic não instalado"}

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"erro": "ANTHROPIC_API_KEY não configurada"}

    SYSTEM_PROMPT = """Você é um ANALISTA/VISTORIADOR de projetos PPCI do Corpo de Bombeiros Militar da Bahia (CBMBA).
Audite a planta de combate a incêndio conforme as ITs do CBMBA.
Retorne APENAS JSON válido (sem markdown, sem texto fora do JSON) com esta estrutura exata:
{
  "confianca_geral": "alta|media|baixa",
  "aprovacao": {"nota": 8.5, "status": "Apto com ressalvas", "resumo": "..."},
  "sugestao_enquadramento": {"grupo": "F", "divisao": "F-8", "descricao": "Restaurante", "risco": "MODERADO", "processo": "Projeto Técnico Completo", "enquadramento_correto": true, "justificativa": "..."},
  "sistemas_auditados": [{"sistema": "Extintores", "it": "IT-04", "exigido": true, "situacao": "conforme", "observacao": "..."}],
  "divergencias_planta_memorial": [],
  "pendencias": [],
  "encontrados": [{"campo": "Área construída", "valor": "500 m²", "confianca": "alta", "origem": "extraido", "fonte": "prancha 01"}]
}"""

    content = []
    for i, pl in enumerate(plantas, 1):
        nome = pl.get("filename", f"planta{i}")
        dados = pl.get("bytes", b"")
        ct = pl.get("content_type", "application/pdf")
        b64 = base64.standard_b64encode(dados).decode()
        content.append({"type": "text", "text": f"--- PLANTA {i}: {nome} ---"})
        if "pdf" in ct or nome.lower().endswith(".pdf"):
            content.append({"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64}})
        else:
            mt = "image/jpeg" if nome.lower().endswith((".jpg",".jpeg")) else "image/png"
            content.append({"type": "image", "source": {"type": "base64", "media_type": mt, "data": b64}})

    if memorial_bytes:
        b64m = base64.standard_b64encode(memorial_bytes).decode()
        content.append({"type": "text", "text": f"--- MEMORIAL: {memorial_filename} ---"})
        content.append({"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64m}})

    content.append({"type": "text", "text": f"Analise as {len(plantas)} prancha(s) em conjunto e retorne apenas o JSON de auditoria."})

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}]
    )

    texto = "".join(b.text for b in response.content if hasattr(b, "text"))
    # Limpa markdown se vier
    texto = texto.strip()
    if texto.startswith("```"):
        texto = texto.split("```")[1]
        if texto.startswith("json"):
            texto = texto[4:]
    resultado = json.loads(texto)
    resultado["_meta"] = {"model": "claude-sonnet-4-6", "arquivos": [p.get("filename") for p in plantas]}
    return resultado


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        api_key_set = bool(os.environ.get("ANTHROPIC_API_KEY"))
        resp = {
            "ai_enabled": api_key_set,
            "api_key_configured": api_key_set,
            "sdk_installed": True,
            "model_default": "claude-sonnet-4-6"
        }
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(resp).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_POST(self):
        try:
            content_type = self.headers.get("Content-Type", "")
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            # Parse multipart
            environ = {
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": content_type,
                "CONTENT_LENGTH": str(length),
            }
            form = cgi.FieldStorage(fp=io.BytesIO(body), environ=environ, keep_blank_values=True)

            plantas = []
            # Aceita "file" e "files"
            for field_name in ["file", "files"]:
                items = form[field_name] if field_name in form else []
                if not isinstance(items, list):
                    items = [items]
                for item in items:
                    if item.filename and item.file:
                        dados = item.file.read()
                        if dados:
                            plantas.append({
                                "bytes": dados,
                                "filename": item.filename,
                                "content_type": item.type or "application/octet-stream"
                            })

            if not plantas:
                raise ValueError("Nenhuma planta enviada")

            memorial_bytes = None
            memorial_filename = None
            memorial_content_type = None
            if "memorial" in form and form["memorial"].filename:
                memorial_bytes = form["memorial"].file.read()
                memorial_filename = form["memorial"].filename
                memorial_content_type = form["memorial"].type

            instrucoes = form.getvalue("instrucoes")

            resultado = analisar_com_ia(
                plantas=plantas,
                memorial_bytes=memorial_bytes,
                memorial_filename=memorial_filename,
                memorial_content_type=memorial_content_type,
                instrucoes=instrucoes
            )

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resultado).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"erro": str(e)}).encode())

import { NextRequest, NextResponse } from 'next/server'
import Anthropic from '@anthropic-ai/sdk'

export const config = {
  api: {
    bodyParser: {
      sizeLimit: '20mb',
    },
  },
}

export const maxDuration = 60

const SYSTEM_PROMPT = `Você é um ANALISTA/VISTORIADOR de projetos PPCI do Corpo de Bombeiros Militar da Bahia (CBMBA), com profundo conhecimento das Instruções Técnicas (ITs).

Sua tarefa é AUDITAR a planta de combate a incêndio e dizer se o projeto está ENQUADRADO CORRETAMENTE e CONFORME as ITs.

Grupos de Ocupação (IT-01 CBMBA):
A: Residencial | B: Hospedagem | C: Comercial varejista | D: Serviços profissionais | E: Educacional | F: Reunião de público (F-8=Restaurante) | G: Serviço automotivo | H: Saúde | I: Industrial | J: Depósitos

Risco: LEVE ≤300 MJ/m² | MODERADO 301-1200 | ELEVADO >1200
Processo: PTS (área≤750m² E altura≤6m E não F/H/I-3) | Projeto Técnico Completo (demais)

NOTA (0-10): comece em 10, desconte por sistemas ausentes (-2 a -3 cada), pendentes (-0.5), enquadramento errado (-1.5). Nunca >6 se faltar sistema obrigatório.
STATUS: "Apto a protocolar" (≥9, sem ausências) | "Apto com ressalvas" (7-8.9) | "Requer correções" (5-6.9) | "Reprovado" (<5)

RETORNE APENAS JSON VÁLIDO, sem markdown, sem texto fora do JSON:
{
  "confianca_geral": "alta",
  "aprovacao": {"nota": 8.5, "status": "Apto com ressalvas", "resumo": "..."},
  "sugestao_enquadramento": {"grupo": "F", "divisao": "F-8", "descricao": "Restaurante", "risco": "MODERADO", "processo": "Projeto Técnico Completo", "enquadramento_correto": true, "justificativa": "..."},
  "sistemas_auditados": [{"sistema": "Extintores", "it": "IT-04", "exigido": true, "situacao": "conforme", "observacao": "..."}],
  "divergencias_planta_memorial": [],
  "pendencias": [],
  "encontrados": [{"campo": "Área construída", "valor": "500 m²", "confianca": "alta", "origem": "extraido", "fonte": "prancha 01"}]
}`

export async function GET() {
  const apiKeySet = !!process.env.ANTHROPIC_API_KEY
  return NextResponse.json({
    ai_enabled: apiKeySet,
    api_key_configured: apiKeySet,
    sdk_installed: true,
    model_default: 'claude-sonnet-4-6',
  })
}

export async function POST(request: NextRequest) {
  try {
    const apiKey = process.env.ANTHROPIC_API_KEY
    if (!apiKey) {
      return NextResponse.json({ erro: 'ANTHROPIC_API_KEY não configurada' }, { status: 500 })
    }

    const formData = await request.formData()
    const content: Anthropic.MessageParam['content'] = []
    const nomes: string[] = []

    // Processa plantas (campo "file" e "files")
    const arquivos: File[] = []
    const fileField = formData.get('file')
    if (fileField instanceof File) arquivos.push(fileField)
    const filesField = formData.getAll('files')
    for (const f of filesField) { if (f instanceof File) arquivos.push(f) }

    if (arquivos.length === 0) {
      return NextResponse.json({ erro: 'Nenhuma planta enviada' }, { status: 400 })
    }

    for (let i = 0; i < arquivos.length; i++) {
      const file = arquivos[i]
      const bytes = await file.arrayBuffer()
      const b64 = Buffer.from(bytes).toString('base64')
      const nome = file.name
      const ct = file.type || 'application/pdf'

      nomes.push(nome)
      content.push({ type: 'text', text: `--- PLANTA ${i + 1}/${arquivos.length}: ${nome} ---` })

      if (ct.includes('pdf') || nome.toLowerCase().endsWith('.pdf')) {
        content.push({
          type: 'document',
          source: { type: 'base64', media_type: 'application/pdf', data: b64 }
        } as Anthropic.DocumentBlockParam)
      } else {
        const mt = nome.toLowerCase().endsWith('.png') ? 'image/png' : 'image/jpeg'
        content.push({
          type: 'image',
          source: { type: 'base64', media_type: mt, data: b64 }
        } as Anthropic.ImageBlockParam)
      }
    }

    // Memorial opcional
    const memorial = formData.get('memorial')
    if (memorial instanceof File && memorial.size > 0) {
      const bytes = await memorial.arrayBuffer()
      const b64 = Buffer.from(bytes).toString('base64')
      content.push({ type: 'text', text: `--- MEMORIAL: ${memorial.name} ---` })
      content.push({
        type: 'document',
        source: { type: 'base64', media_type: 'application/pdf', data: b64 }
      } as Anthropic.DocumentBlockParam)
    }

    const instrucoes = formData.get('instrucoes')
    content.push({
      type: 'text',
      text: `Analise as ${nomes.length} prancha(s) em conjunto (${nomes.join(', ')}) e retorne apenas o JSON de auditoria PPCI conforme as ITs do CBMBA.${instrucoes ? `\n\nInstruções adicionais: ${instrucoes}` : ''}`
    })

    const client = new Anthropic({ apiKey })
    const response = await client.messages.create({
      model: 'claude-sonnet-4-6',
      max_tokens: 8000,
      system: SYSTEM_PROMPT,
      messages: [{ role: 'user', content }],
    })

    let texto = response.content
      .filter(b => b.type === 'text')
      .map(b => (b as Anthropic.TextBlock).text)
      .join('')
      .trim()

    // Remove markdown se vier
    if (texto.startsWith('```')) {
      texto = texto.replace(/^```(?:json)?\n?/, '').replace(/\n?```$/, '').trim()
    }

    // Extrai JSON mesmo que o texto esteja truncado
    const start = texto.indexOf('{')
    if (start === -1) throw new Error('IA não retornou JSON válido')
    
    let jsonStr = texto.slice(start)
    let resultado: Record<string, unknown>
    
    try {
      resultado = JSON.parse(jsonStr)
    } catch {
      // Tenta fechar o JSON truncado
      const depth = (jsonStr.match(/{/g)||[]).length - (jsonStr.match(/}/g)||[]).length
      jsonStr += '}'.repeat(Math.max(depth, 1))
      try {
        resultado = JSON.parse(jsonStr)
      } catch {
        throw new Error(`JSON inválido retornado pela IA: ${jsonStr.slice(0, 200)}`)
      }
    }
    resultado._meta = {
      model: 'claude-sonnet-4-6',
      arquivos: nomes,
      input_tokens: response.usage.input_tokens,
      output_tokens: response.usage.output_tokens,
    }

    return NextResponse.json(resultado)

  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : 'Erro desconhecido'
    return NextResponse.json({ erro: msg }, { status: 500 })
  }
}

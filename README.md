# PPCI SaaS — Sistema de Dimensionamento de Projetos PPCI

## Prevenção e Proteção Contra Incêndio e Pânico — CBMBA

Plataforma SaaS para dimensionamento automático de projetos de prevenção contra incêndio,
baseada nas Instruções Técnicas do Corpo de Bombeiros Militar da Bahia.

---

## Arquitetura do Projeto

```
ppci-saas/
├── database/
│   └── schema.sql              # Schema completo do Supabase (PostgreSQL)
│
├── backend/
│   ├── main.py                 # FastAPI — servidor principal + endpoints
│   │
│   ├── normas/                 # Regras normativas (arquivos configuráveis)
│   │   ├── ocupacoes.py        # IT-01: Grupos e divisões de ocupação
│   │   ├── riscos.py           # IT-01/14: Classificação de risco
│   │   ├── sistemas_exigidos.py # IT-01: Sistemas de proteção exigidos
│   │   └── tabelas_it.py       # Tabelas de referência das ITs
│   │
│   ├── calculos/               # Motores de dimensionamento
│   │   ├── classificacao.py    # Motor de classificação geral
│   │   ├── saida_emergencia.py # IT-11: Saídas de emergência
│   │   ├── extintores.py       # IT-04: Extintores de incêndio
│   │   ├── hidrantes.py        # IT-17: Hidrantes e mangotinhos
│   │   └── reserva_bomba.py    # IT-17/22: Reserva técnica + bomba
│   │
│   └── exports/                # Geração de documentos
│       ├── excel_export.py     # Planilha .xlsx editável
│       └── pdf_export.py       # Memorial descritivo + relatório PDF
│
└── frontend/
    └── ppci-saas-app.jsx       # Aplicação React completa
```

---

## Banco de Dados (Supabase)

### Tabelas

| Tabela | Descrição |
|--------|-----------|
| `perfis` | Extensão de `auth.users` com dados profissionais |
| `projetos` | Projetos PPCI com status e versionamento |
| `edificacoes` | Dados técnicos completos da edificação |
| `classificacoes` | Resultado da classificação automática |
| `calculos_saida_emergencia` | Dimensionamento IT-11 |
| `calculos_extintores` | Dimensionamento IT-04 |
| `calculos_hidrantes` | Dimensionamento IT-17 |
| `calculos_reserva_tecnica` | Volume RTI (IT-17/22) |
| `calculos_bombas_incendio` | Potência de bombas (IT-22) |
| `documentos_gerados` | Registro de documentos exportados |
| `versoes_projeto` | Histórico de versões (snapshots JSON) |

### Setup no Supabase

1. Crie um projeto em https://supabase.com
2. Vá em SQL Editor
3. Execute o arquivo `database/schema.sql`
4. As políticas de RLS já estão configuradas

---

## Backend (FastAPI)

### Instalação

```bash
cd backend
pip install fastapi uvicorn pydantic openpyxl reportlab
```

### Execução

```bash
uvicorn backend.main:app --reload --port 8000
```

### Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/normas/grupos` | Lista grupos de ocupação |
| GET | `/api/normas/divisoes/{grupo}` | Lista divisões de um grupo |
| POST | `/api/calculos/classificacao` | Classifica a edificação |
| POST | `/api/calculos/saida-emergencia` | Calcula saídas de emergência |
| POST | `/api/calculos/extintores` | Calcula extintores |
| POST | `/api/calculos/hidrantes` | Calcula hidrantes |
| POST | `/api/calculos/reserva-tecnica` | Calcula reserva técnica |
| POST | `/api/calculos/bomba-incendio` | Calcula bomba de incêndio |
| POST | `/api/calculos/projeto-completo` | Executa todos os cálculos |

### Estrutura de Normas (pasta `/normas`)

Os arquivos de normas são **configuráveis** e separados do código de cálculo:

- **`ocupacoes.py`** — Tabela completa de ocupações (A a J), populações por m² e cargas de incêndio
- **`riscos.py`** — Faixas de risco (Leve/Moderado/Elevado) e classes de incêndio
- **`sistemas_exigidos.py`** — Regras condicionais para exigência de cada sistema
- **`tabelas_it.py`** — Valores numéricos das ITs (larguras, vazões, pressões, volumes)

Para atualizar conforme novas ITs, basta editar os dicionários nesses arquivos.

---

## Frontend (React)

### Páginas Implementadas

1. **Login / Cadastro** — Tela de autenticação com Supabase
2. **Dashboard** — Cards estatísticos + tabela de projetos
3. **Novo Projeto** — Formulário multi-step com:
   - Dados da edificação
   - Classificação (grupo/divisão)
   - Revisão com preview dos sistemas exigidos
4. **Cálculos** — Abas com cada módulo de dimensionamento:
   - Classificação
   - Saída de emergência (IT-11)
   - Extintores (IT-04)
   - Hidrantes (IT-17)
   - Reserva técnica (IT-17/22)
   - Bomba de incêndio (IT-22)
5. **Revisão** — Visão consolidada de todos os resultados
6. **Exportar** — Memorial PDF, planilha Excel, relatório técnico

### Setup com Next.js

```bash
npx create-next-app@latest ppci-frontend --typescript --tailwind
cd ppci-frontend
npm install lucide-react
# Copie o conteúdo do JSX para src/app/page.tsx
```

---

## ITs do CBMBA Implementadas

| IT | Assunto | Módulo |
|----|---------|--------|
| IT-01 | Procedimentos Administrativos | classificacao.py |
| IT-04 | Extintores de Incêndio | extintores.py |
| IT-11 | Saídas de Emergência | saida_emergencia.py |
| IT-14 | Carga de Incêndio | riscos.py |
| IT-17 | Hidrantes e Mangotinhos | hidrantes.py |
| IT-22 | Bombas de Incêndio | reserva_bomba.py |

---

## Próximos Passos

- [ ] Integração Supabase Auth no frontend
- [ ] API calls reais (fetch) conectando front ↔ back
- [ ] Upload e armazenamento dos documentos gerados (Supabase Storage)
- [ ] Sistema de assinatura mensal (Stripe)
- [ ] Módulo de chuveiros automáticos (IT-23)
- [ ] Módulo de sinalização (IT-20)
- [ ] Módulo de iluminação de emergência (IT-18)
- [ ] Geração de plantas baixas esquemáticas
- [ ] Multi-tenancy para escritórios de engenharia
- [ ] Painel administrativo

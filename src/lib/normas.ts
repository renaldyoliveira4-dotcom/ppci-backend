// ---- NORMAS CBMBA ----
// Dados extraídos das ITs do Corpo de Bombeiros Militar da Bahia

export const GRUPOS: Record<string, { nome: string; divisoes: Record<string, string> }> = {
  A: { nome: "Residencial", divisoes: { "A-1": "Habitação unifamiliar", "A-2": "Habitação multifamiliar", "A-3": "Habitação coletiva" } },
  B: { nome: "Serviços de Hospedagem", divisoes: { "B-1": "Hotel / Motel", "B-2": "Apart-hotel" } },
  C: { nome: "Comercial Varejista", divisoes: { "C-1": "Comércio em geral", "C-2": "Supermercado / Hipermercado", "C-3": "Shopping Center" } },
  D: { nome: "Serviços Profissionais", divisoes: { "D-1": "Escritórios e serviços gerais", "D-2": "Agência bancária", "D-3": "Oficinas e serviços técnicos", "D-4": "Laboratórios" } },
  E: { nome: "Educacional e Cultura Física", divisoes: { "E-1": "Escola / Universidade", "E-2": "Escola especial / Idiomas", "E-3": "Academia / Esportes", "E-4": "Ensino profissional", "E-5": "Creche", "E-6": "Outros" } },
  F: { nome: "Locais de Reunião de Público", divisoes: { "F-1": "Biblioteca / Museu", "F-2": "Igreja / Templo", "F-3": "Ginásio / Estádio", "F-4": "Terminal de passageiros", "F-5": "Cinema / Teatro", "F-6": "Boate / Bar", "F-7": "Rodeio / Circo", "F-8": "Restaurante / Lanchonete", "F-9": "Parques e zoológicos", "F-11": "Clube / Casa de festas" } },
  G: { nome: "Serviços Automotivos", divisoes: { "G-1": "Posto de combustível", "G-2": "Estacionamento", "G-3": "Comércio de combustíveis", "G-4": "Oficina automotiva", "G-5": "Hangar", "G-6": "Porto" } },
  H: { nome: "Serviços de Saúde", divisoes: { "H-1": "Veterinário", "H-2": "Clínica geriátrica / Asilo", "H-3": "Hospital / Pronto-socorro", "H-4": "Militar / Policial", "H-5": "Presídio", "H-6": "Consultório / Ambulatório" } },
  I: { nome: "Industrial", divisoes: { "I-1": "Indústria de baixo risco", "I-2": "Indústria de médio risco", "I-3": "Indústria de alto risco" } },
  J: { nome: "Depósitos", divisoes: { "J-1": "Depósito baixo risco", "J-2": "Depósito médio risco", "J-3": "Depósito alto risco", "J-4": "Depósito especial" } },
  L: { nome: "Explosivos", divisoes: { "L-1": "Fogos de artifício (varejo)", "L-2": "Fabricação de explosivos" } },
  M: { nome: "Especial", divisoes: { "M-1": "Subterrâneo / Túnel", "M-2": "Inflamáveis líquidos/gasosos", "M-3": "Central de energia", "M-4": "Construção / Canteiro", "M-6": "Área de terra selvagem", "M-7": "Pátio de containers" } },
}

export const POP_M2: Record<string, number> = {
  "A-1": 0.05, "A-2": 0.05, "A-3": 0.1,
  "B-1": 0.1, "B-2": 0.1,
  "C-1": 0.1, "C-2": 0.2, "C-3": 0.2,
  "D-1": 0.1, "D-2": 0.1, "D-3": 0.07,
  "E-1": 0.5, "E-2": 0.25, "E-3": 0.25, "E-4": 0.25, "E-5": 0.5, "E-6": 0.25,
  "F-1": 0.3, "F-2": 0.5, "F-3": 0.5, "F-4": 0.2, "F-5": 1, "F-6": 1, "F-7": 0.5, "F-8": 0.3,
  "G-1": 0.03, "G-2": 0.03, "G-3": 0.05, "G-4": 0.07,
  "H-1": 0.1, "H-2": 0.15, "H-3": 0.15,
  "I-1": 0.05, "I-2": 0.05, "I-3": 0.03,
  "J-1": 0.02, "J-2": 0.02,
}

export const CARGA: Record<string, number> = {
  "A-1": 300, "A-2": 300, "A-3": 300,
  "B-1": 500, "B-2": 500,
  "C-1": 400, "C-2": 800, "C-3": 600,
  "D-1": 700, "D-2": 400, "D-3": 800, "D-4": 500,
  "E-1": 300, "E-2": 300, "E-3": 200, "E-4": 300, "E-5": 400, "E-6": 400,
  "F-1": 300, "F-2": 200, "F-3": 150, "F-4": 200, "F-5": 400, "F-6": 300, "F-7": 300, "F-8": 600, "F-9": 300, "F-11": 600,
  "G-1": 200, "G-2": 200, "G-3": 300, "G-4": 800, "G-5": 1000,
  "H-1": 300, "H-2": 350, "H-3": 300, "H-4": 300, "H-5": 300, "H-6": 300,
  "I-1": 300, "I-2": 1200, "I-3": 2000,
  "J-1": 300, "J-2": 600, "J-3": 1200, "J-4": 2000,
}

export type RiscoNivel = 1 | 2 | 3 | 4

export function risco(carga: number): { nivel: RiscoNivel; label: string } {
  if (carga <= 300) return { nivel: 1, label: "Risco Baixo (≤300 MJ/m²)" }
  if (carga <= 1200) return { nivel: 2, label: "Risco Médio (301–1200 MJ/m²)" }
  if (carga <= 2400) return { nivel: 3, label: "Risco Alto (1201–2400 MJ/m²)" }
  return { nivel: 4, label: "Risco Muito Alto (>2400 MJ/m²)" }
}

export function sistemasExigidos(
  area: number, altura: number, grupo: string, divisao: string,
  riscoNivel: RiscoNivel, possuiSubsolo: boolean, populacao: number, pavimentos: number
): string[] {
  const s: string[] = []
  if (area > 0) s.push("EXTINTORES")
  if (altura > 6 || area > 750) s.push("ILUMINACAO")
  if (altura > 6 || area > 750) s.push("SINALIZACAO")
  if (altura >= 12 || area > 1500) s.push("ALARME")
  if (altura >= 12 || area > 1500 || grupo === "F") s.push("HIDRANTES")
  if (populacao >= 30) s.push("BRIGADA")
  if (possuiSubsolo) s.push("PRESSURIZACAO")
  if (divisao === "G-1" || divisao === "M-2") s.push("GLP")
  if (riscoNivel >= 3 || altura > 23) s.push("SPRINKLERS")
  if (altura > 30) s.push("SPDA")
  return s
}

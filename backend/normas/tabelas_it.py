"""
NORMAS - Tabelas de Referência das Instruções Técnicas
Baseado nas ITs do CBMBA

INSTRUÇÕES PARA ATUALIZAÇÃO:
- Cada tabela é um dicionário configurável
- Atualizar conforme revisões das ITs
"""

# ============================================================
# IT-11: Saídas de Emergência
# ============================================================

# Capacidade de uma unidade de passagem (pessoas/min) por tipo de uso
CAPACIDADE_UNIDADE_PASSAGEM = {
    "ACESSO": {"capacidade": 60, "descricao": "Acessos e descargas"},
    "ESCADA": {"capacidade": 45, "descricao": "Escadas"},
    "RAMPA": {"capacidade": 45, "descricao": "Rampas"},
    "PORTA": {"capacidade": 100, "descricao": "Portas"},
}

# Largura mínima das saídas de emergência por ocupação
LARGURA_MINIMA_SAIDA = {
    "A": 1.10,   # Residencial
    "B": 1.10,   # Hospedagem
    "C": 1.65,   # Comercial (corredores e escadas com lotação > 50)
    "D": 1.10,   # Serviços profissionais
    "E": 1.65,   # Educacional
    "F": 1.65,   # Reunião de público
    "G": 1.10,   # Automotivo
    "H": 2.20,   # Saúde
    "I": 1.10,   # Industrial
    "J": 1.10,   # Depósitos
}

# Distância máxima de caminhamento (metros) - IT-11 Tabela 3
DISTANCIA_MAXIMA_CAMINHAMENTO = {
    "SEM_CHUVEIROS": {
        "UNICA_SAIDA": 15.0,
        "MAIS_DE_UMA_SAIDA": 30.0,
    },
    "COM_CHUVEIROS": {
        "UNICA_SAIDA": 25.0,
        "MAIS_DE_UMA_SAIDA": 45.0,
    },
}

# Número mínimo de saídas por pavimento
NUMERO_MINIMO_SAIDAS = [
    {"populacao_max": 50, "saidas": 1},
    {"populacao_max": 200, "saidas": 2},
    {"populacao_max": 500, "saidas": 3},
    {"populacao_max": 99999, "saidas": 4},
]

# Tipos de escada por altura/grupo
TIPO_ESCADA = {
    "COMUM": {
        "descricao": "Escada comum (não enclausurada)",
        "altura_max": 6.0,
        "aplicacao": "Edificações com até 6 m de altura",
    },
    "ENCLAUSURADA_PROTEGIDA": {
        "descricao": "Escada enclausurada protegida (EP)",
        "altura_max": 12.0,
        "aplicacao": "Edificações de 6 m até 12 m de altura",
    },
    "ENCLAUSURADA_PROVA_FUMACA": {
        "descricao": "Escada enclausurada à prova de fumaça (PF)",
        "altura_max": 999.0,
        "aplicacao": "Edificações acima de 12 m de altura",
    },
}

# ============================================================
# IT-04: Extintores de Incêndio
# ============================================================

# Área máxima de proteção por extintor e risco
AREA_PROTECAO_EXTINTOR = {
    "LEVE": {"area_maxima": 500, "distancia_maxima": 25},
    "MODERADO": {"area_maxima": 250, "distancia_maxima": 20},
    "ELEVADO": {"area_maxima": 150, "distancia_maxima": 15},
}

# Tipos de extintores recomendados por classe
EXTINTORES_POR_CLASSE = {
    "A": [
        {"tipo": "Água pressurizada", "capacidade": "10 L", "unidades_extintoras": 1},
        {"tipo": "Pó químico ABC", "capacidade": "4 kg", "unidades_extintoras": 2},
        {"tipo": "Pó químico ABC", "capacidade": "6 kg", "unidades_extintoras": 3},
    ],
    "B": [
        {"tipo": "CO2", "capacidade": "6 kg", "unidades_extintoras": 2},
        {"tipo": "Pó químico BC", "capacidade": "4 kg", "unidades_extintoras": 2},
        {"tipo": "Pó químico ABC", "capacidade": "6 kg", "unidades_extintoras": 3},
    ],
    "C": [
        {"tipo": "CO2", "capacidade": "6 kg", "unidades_extintoras": 2},
        {"tipo": "Pó químico BC", "capacidade": "4 kg", "unidades_extintoras": 2},
        {"tipo": "Pó químico ABC", "capacidade": "6 kg", "unidades_extintoras": 3},
    ],
}

# ============================================================
# IT-17: Hidrantes e Mangotinhos
# ============================================================

# Tipos de sistema de hidrantes
TIPOS_SISTEMA_HIDRANTE = {
    "TIPO_1": {
        "nome": "Tipo 1 - Mangotinho",
        "diametro_mangueira": "25 mm (1\")",
        "comprimento_mangueira": 30,
        "tipo_esguicho": "Regulável",
        "vazao_minima_lpm": 80,
        "pressao_minima_mca": 10,
        "aplicacao": "Risco leve, até 2 hidrantes simultâneos",
        "numero_hidrantes_simultaneos": 2,
    },
    "TIPO_2": {
        "nome": "Tipo 2 - Mangueira 40mm",
        "diametro_mangueira": "40 mm (1½\")",
        "comprimento_mangueira": 30,
        "tipo_esguicho": "Jato compacto 16mm ou regulável",
        "vazao_minima_lpm": 150,
        "pressao_minima_mca": 15,
        "aplicacao": "Risco moderado, 2 hidrantes simultâneos",
        "numero_hidrantes_simultaneos": 2,
    },
    "TIPO_3": {
        "nome": "Tipo 3 - Mangueira 65mm",
        "diametro_mangueira": "65 mm (2½\")",
        "comprimento_mangueira": 30,
        "tipo_esguicho": "Jato compacto 25mm ou regulável",
        "vazao_minima_lpm": 300,
        "pressao_minima_mca": 35,
        "aplicacao": "Risco elevado, 3 hidrantes simultâneos",
        "numero_hidrantes_simultaneos": 3,
    },
}

# Seleção do tipo de sistema por risco
SISTEMA_HIDRANTE_POR_RISCO = {
    "LEVE": "TIPO_1",
    "MODERADO": "TIPO_2",
    "ELEVADO": "TIPO_3",
}

# ============================================================
# IT-22 / IT-17: Reserva Técnica de Incêndio
# ============================================================

# Tempo de combate por tipo de sistema (em minutos)
TEMPO_COMBATE = {
    "TIPO_1": 60,
    "TIPO_2": 60,
    "TIPO_3": 60,
}

# Volume mínimo de reserva (litros)
VOLUME_MINIMO_RESERVA = {
    "TIPO_1": 5000,
    "TIPO_2": 8000,
    "TIPO_3": 18000,
}

# ============================================================
# IT-22: Bombas de Incêndio
# ============================================================

# Coeficientes para cálculo de potência de bomba
EFICIENCIA_BOMBA = 0.65  # Rendimento médio
FATOR_SEGURANCA_BOMBA = 1.25  # Margem de segurança

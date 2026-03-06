# =========================
# config.py - Auraxis robusto
# =========================

# =========================
# Chaves de API
# =========================
API_KEYS = {
    "alpha_vantage": "K3UBBNQ1VU646E9T",
    "twelvedata": "b5291ab39a2b4a91927d63e375cccf6e",
    "fcs_api": "8vekAGcxDcYad58mqY5VNp8c2vAygnx4M"
}

# =========================
# Parâmetros de trading
# =========================
TRADING_CONFIG = {
    "pares": ["EUR/USD"],  # Apenas EUR/USD
    "entrada_dupla": True,  # Habilita entrada externa + interna
    "limites_zona": {       # Zonas para entradas, stop e take
        "entrada": {
            "superior": 0.0003,  # máxima diferença para entrada interna
            "inferior": 0.0001   # mínima diferença para entrada interna
        },
        "stop": {
            "superior": 0.0012,  # máxima distância do preço de entrada
            "inferior": 0.0008   # mínima distância do preço de entrada
        },
        "take": {
            "superior": 0.0025,  # máxima distância do preço de entrada
            "inferior": 0.0015   # mínima distância do preço de entrada
        }
    },
    "rr_min": 1.5,        # RR mínimo aceito
    "score_default": 80,  # Score inicial padrão
    "fragmentacao_segundos": 5  # Atualização de candles em segundos
}

# =========================
# Configurações de fallback e limites
# =========================
FALLBACK_CONFIG = {
    "usar_yfinance": True,   # Só ativa se todas as APIs falharem
    "ultimo_candle_padrao": 1.16100  # fallback interno se todas falharem
}

# =========================
# Configurações de interface
# =========================
UI_CONFIG = {
    "cores": {
        "background": "#121212",
        "texto": "#FFFFFF",
        "positivo": "#00FF00",
        "negativo": "#FF0000",
        "entrada": "#1E90FF",
        "take": "#FFD700",
        "stop": "#FF4500"
    },
    "font_size": {
        "principal": 20,
        "secundario": 16
    },
    "abas": ["Mercado", "Oportunidades", "Histórico"]
}

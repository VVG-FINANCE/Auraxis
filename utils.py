# =========================
# utils.py - Auraxis robusto
# =========================
from config import TRADING_CONFIG

# =========================
# Calcula Risk/Reward
# =========================
def calcular_rr(entrada, stop, take):
    """
    Calcula RR (Risk/Reward)
    """
    risco = abs(entrada - stop)
    ganho = abs(take - entrada)
    if risco == 0:
        return 0
    return ganho / risco

# =========================
# Ajusta score combinando base + ML + Bayes
# =========================
def score_final(score_base, score_ml, peso_ml=0.6):
    """
    Combina score base do candle + score do ML
    peso_ml: quanto o ML influencia
    """
    return round(score_base*(1-peso_ml) + score_ml*peso_ml, 2)

# =========================
# Limita valores dentro da zona definida
# =========================
def limitar_valor(valor, zona):
    """
    Limita valor dentro de zona (inferior/superior)
    """
    if valor < zona["inferior"]:
        return zona["inferior"]
    if valor > zona["superior"]:
        return zona["superior"]
    return valor

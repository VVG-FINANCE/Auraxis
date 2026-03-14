# utils.py
# Funções auxiliares para CoreEngine, DataManager, Monte Carlo e Bayes
# Inclui RR, score final, pips, normalização e outros cálculos

def calculate_rr(entry_price, sl, tp):
    """
    Calcula Risk/Reward ratio
    entry_price: preço de entrada
    sl: stop loss
    tp: take profit
    Retorna: RR ratio
    """
    risk = abs(entry_price - sl)
    reward = abs(tp - entry_price)
    if risk == 0:
        return float('inf')
    return reward / risk

def normalize_score(score):
    """
    Normaliza score para 0-100
    """
    return max(0, min(100, score))

def adjust_price_by_pips(price, pips):
    """
    Ajusta preço em ±pips (ex: 30 pips = 0.0030)
    """
    return price + pips

def compute_final_score(opportunity):
    """
    Combina ajustes ML, Monte Carlo e Bayes para score final
    """
    base = opportunity.get('score', 50)
    mc_adj = opportunity.get('mc_adjustment', 0)
    bayes_adj = opportunity.get('bayes_adjustment', 0)
    final_score = normalize_score(base + mc_adj + bayes_adj)
    return final_score

def rolling_zscore(series, window=20):
    """
    Calcula Z-score de uma série temporal
    """
    mean = series.rolling(window).mean()
    std = series.rolling(window).std()
    zscore = (series - mean) / std
    return zscore

def log_return(series):
    """
    Calcula retorno logarítmico de uma série de preços
    """
    return (series / series.shift(1)).apply(lambda x: np.log(x))

# Exemplo de uso:
# rr = calculate_rr(entry_price=1.1000, sl=1.0980, tp=1.1040)
# score = compute_final_score(opportunity)

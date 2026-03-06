# =========================
# candle_analysis.py - Auraxis robusto
# =========================
from datetime import datetime
from config import TRADING_CONFIG, UI_CONFIG
from utils import calcular_rr, score_final

class CandleAnalysis:
    """
    Analisa candles e gera oportunidades robustas para o Auraxis
    """

    def __init__(self):
        self.patterns = ["bullish_engulfing", "bearish_engulfing", "pin_bar", "hammer", "doji"]
        self.rr_min = TRADING_CONFIG["rr_min"]
        self.limites = TRADING_CONFIG["limites_zona"]
        self.ultimo_candle = None

    # =========================
    # Detecta padrões de candle
    # =========================
    def detectar_padroes(self, candle_atual, candle_anterior):
        padroes_detectados = []

        # Bullish Engulfing
        if candle_anterior["close"] < candle_anterior["open"] and candle_atual["close"] > candle_atual["open"] and candle_atual["close"] > candle_anterior["open"]:
            padroes_detectados.append("bullish_engulfing")

        # Bearish Engulfing
        if candle_anterior["close"] > candle_anterior["open"] and candle_atual["close"] < candle_atual["open"] and candle_atual["close"] < candle_anterior["open"]:
            padroes_detectados.append("bearish_engulfing")

        # Pin Bar
        corpo = abs(candle_atual["close"] - candle_atual["open"])
        sombra_sup = candle_atual["high"] - max(candle_atual["close"], candle_atual["open"])
        sombra_inf = min(candle_atual["close"], candle_atual["open"]) - candle_atual["low"]
        if sombra_sup > 2*corpo or sombra_inf > 2*corpo:
            padroes_detectados.append("pin_bar")

        # Martelo simples
        if corpo < 0.0005 and sombra_inf > 2*corpo:
            padroes_detectados.append("hammer")

        # Doji
        if corpo < 0.0002:
            padroes_detectados.append("doji")

        return padroes_detectados

    # =========================
    # Gera oportunidade robusta
    # =========================
    def gerar_oportunidade(self, candle):
        candle_anterior = self.ultimo_candle if self.ultimo_candle else candle
        padroes = self.detectar_padroes(candle, candle_anterior)
        if not padroes:
            self.ultimo_candle = candle
            return None

        preco = candle["close"]
        tipo = "Compra" if "bullish_engulfing" in padroes or "pin_bar" in padroes else "Venda"

        # =========================
        # Entradas dupla com limites de zona
        # =========================
        zona_entrada = self.limites["entrada"]
        if tipo == "Compra":
            entrada_externa = round(preco, 5)
            entrada_interna = round(preco - (zona_entrada["inferior"] + (zona_entrada["superior"]-zona_entrada["inferior"])/2), 5)
            stop = round(preco - (self.limites["stop"]["inferior"] + (self.limites["stop"]["superior"]-self.limites["stop"]["inferior"])/2), 5)
            take = round(preco + (self.limites["take"]["inferior"] + (self.limites["take"]["superior"]-self.limites["take"]["inferior"])/2), 5)
        else:
            entrada_externa = round(preco, 5)
            entrada_interna = round(preco + (zona_entrada["inferior"] + (zona_entrada["superior"]-zona_entrada["inferior"])/2), 5)
            stop = round(preco + (self.limites["stop"]["inferior"] + (self.limites["stop"]["superior"]-self.limites["stop"]["inferior"])/2), 5)
            take = round(preco - (self.limites["take"]["inferior"] + (self.limites["take"]["superior"]-self.limites["take"]["inferior"])/2), 5)

        rr = calcular_rr(entrada_externa, stop, take)
        if rr < self.rr_min:
            self.ultimo_candle = candle
            return None

        # Score inicial simplificado
        score = 80 if "bullish_engulfing" in padroes or "bearish_engulfing" in padroes else 70

        # Tendência: a favor ou contra
        tendencia = "A favor" if (tipo=="Compra" and preco >= candle_anterior["close"]) or (tipo=="Venda" and preco <= candle_anterior["close"]) else "Contra"

        oportunidade = {
            "tipo": tipo,
            "entrada_externa": entrada_externa,
            "entrada_interna": entrada_interna,
            "stop": stop,
            "take": take,
            "rr": round(rr,2),
            "score": score,
            "tendencia": tendencia,
            "padroes": padroes,
            "time": datetime.now().isoformat()
        }

        self.ultimo_candle = candle
        return oportunidade

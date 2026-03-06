# =========================
# data_manager.py - Auraxis robusto
# =========================
import os
import requests
import yfinance as yf
from datetime import datetime
from config import API_KEYS, TRADING_CONFIG, FALLBACK_CONFIG

class DataManager:
    """
    Gerencia todas as fontes de dados do Auraxis:
    - Alpha Vantage
    - Twelve Data
    - FCS API
    - Fallback com yfinance
    - Geração de candles e histórico
    """

    def __init__(self):
        # Chaves
        self.alpha_key = os.environ.get("ALPHA_VANTAGE_KEY", API_KEYS["alpha_vantage"])
        self.twelve_key = os.environ.get("TWELVE_DATA_KEY", API_KEYS["twelvedata"])
        self.fcs_key = os.environ.get("FCS_API_KEY", API_KEYS["fcs_api"])
        
        # Histórico
        self.ultimo_candle = None
        self.candles = []

        # Config fallback
        self.fallback_yf = FALLBACK_CONFIG["usar_yfinance"]
        self.candle_padrao = FALLBACK_CONFIG["ultimo_candle_padrao"]

    # =========================
    # APIs principais
    # =========================
    def obter_preco_alpha(self):
        try:
            url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=EUR&to_symbol=USD&interval=1min&apikey={self.alpha_key}"
            r = requests.get(url, timeout=5)
            data = r.json()
            ultimo_valor = list(data['Time Series FX (1min)'].values())[0]['4. close']
            return float(ultimo_valor)
        except Exception:
            return None

    def obter_preco_twelve(self):
        try:
            url = f"https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=1min&apikey={self.twelve_key}"
            r = requests.get(url, timeout=5)
            data = r.json()
            ultimo_valor = float(data['values'][0]['close'])
            return ultimo_valor
        except Exception:
            return None

    def obter_preco_fcs(self):
        try:
            url = f"https://api-v4.fcsapi.com/forex/list?access_key={self.fcs_key}"
            r = requests.get(url, timeout=5)
            data = r.json()
            eurusd = next((item for item in data['response'] if item['symbol'] == 'EUR/USD'), None)
            return float(eurusd['close']) if eurusd else None
        except Exception:
            return None

    # =========================
    # Fallback yfinance
    # =========================
    def obter_preco_yfinance(self):
        try:
            ticker = yf.Ticker("EURUSD=X")
            data = ticker.history(period="1d", interval="1m")
            ultimo = data['Close'].iloc[-1]
            return float(ultimo)
        except Exception:
            return None

    # =========================
    # Preço atual com fallback automático
    # =========================
    def obter_preco_atual(self):
        """
        Retorna preço do EUR/USD usando primeira fonte disponível
        """
        for func in [self.obter_preco_alpha, self.obter_preco_twelve, self.obter_preco_fcs]:
            preco = func()
            if preco is not None:
                self.ultimo_candle = preco
                return preco

        if self.fallback_yf:
            preco = self.obter_preco_yfinance()
            if preco:
                self.ultimo_candle = preco
                return preco

        # fallback interno
        return self.ultimo_candle if self.ultimo_candle else self.candle_padrao

    # =========================
    # Geração de candles
    # =========================
    def gerar_candle(self):
        """
        Gera candle simplificado com preço atual
        """
        preco = self.obter_preco_atual()
        candle = {
            "open": self.candles[-1]["close"] if self.candles else preco,
            "high": max(preco, self.candles[-1]["high"]) if self.candles else preco,
            "low": min(preco, self.candles[-1]["low"]) if self.candles else preco,
            "close": preco,
            "time": datetime.now().isoformat()
        }
        self.candles.append(candle)
        if len(self.candles) > 200:
            self.candles.pop(0)
        return candle

    def obter_candles(self, n=100):
        """
        Retorna últimos n candles, gerando novos se necessário
        """
        while len(self.candles) < n:
            self.gerar_candle()
        return self.candles[-n:]

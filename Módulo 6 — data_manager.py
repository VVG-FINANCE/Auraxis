# data_manager.py
# Coleta dados do mercado, fallback inteligente e ajuste de pips
# Integra com HistoryManager e armazena histórico em SQLite

import time
import requests
import yfinance as yf
import pandas as pd
from data_pipeline.history_manager import HistoryManager

class DataManager:
    def __init__(self, history_manager, pip_adjustment=0.0):
        """
        history_manager: objeto HistoryManager para persistência
        pip_adjustment: ajuste manual em pips (ex: 30 pips = 0.0030)
        """
        self.history_manager = history_manager
        self.pip_adjustment = pip_adjustment
        self.fallback_intervals = [5, 10, 15, 30, 60]  # em segundos
        self.current_interval_index = 0

    def fetch_exchangerate_api(self):
        try:
            url = "https://api.exchangerate.host/latest?base=EUR&symbols=USD"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            price = data['rates']['USD']
            return price
        except:
            return None

    def fetch_frankfurter(self):
        try:
            url = "https://api.frankfurter.app/latest?from=EUR&to=USD"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            price = data['rates']['USD']
            return price
        except:
            return None

    def fetch_yfinance(self):
        try:
            ticker = yf.Ticker("EURUSD=X")
            df = ticker.history(period="1d", interval="1m")
            if not df.empty:
                price = df['Close'].iloc[-1]
                return price
            return None
        except:
            return None

    def fetch_price(self):
        """
        Coleta preço usando fallback progressivo
        """
        fetchers = [self.fetch_exchangerate_api, self.fetch_frankfurter, self.fetch_yfinance]
        price = None

        for fetch in fetchers:
            price = fetch()
            if price is not None:
                break

        if price is None:
            # Se falhou em todas, espera intervalo atual e tenta de novo
            time.sleep(self.fallback_intervals[self.current_interval_index])
            self.current_interval_index = min(self.current_interval_index + 1, len(self.fallback_intervals) - 1)
            return self.fetch_price()
        else:
            # Reset interval se sucesso
            self.current_interval_index = 0
            # Ajuste de pips
            price += self.pip_adjustment
            return price

    def update_candle(self):
        """
        Cria ou atualiza candle 1 minuto com o preço atual
        """
        price = self.fetch_price()
        timestamp = pd.Timestamp.utcnow().floor('T')  # arredonda para minuto

        # Tenta atualizar último candle
        last_candle = self.history_manager.get_last_candle('1min')
        if last_candle is not None and last_candle['timestamp'] == timestamp:
            # Atualiza high, low e close
            high = max(last_candle['high'], price)
            low = min(last_candle['low'], price)
            self.history_manager.update_candle(timestamp, open_price=last_candle['open'],
                                               high=high, low=low, close=price, volume=last_candle['volume'])
        else:
            # Cria novo candle
            self.history_manager.insert_candle(timestamp, open_price=price, high=price,
                                               low=price, close=price, volume=0)

        return price

    def run_loop(self):
        """
        Loop contínuo para atualização de candles
        """
        while True:
            price = self.update_candle()
            print(f"[DataManager] Candle atualizado: {price}")
            time.sleep(60)  # atualiza a cada 1 minuto

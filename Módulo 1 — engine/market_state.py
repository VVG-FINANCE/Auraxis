# engine/market_state.py
# Responsável por coletar o estado do mercado e gerar indicadores multitimeframe (retrovisor)
# Alimenta o motor central com informações de tendência, volatilidade e estrutura

import pandas as pd
import numpy as np

class MarketState:
    def __init__(self, history_manager, timeframes=None):
        """
        history_manager: objeto que gerencia histórico em SQLite
        timeframes: lista de timeframes para retrovisor multitimeframe
        """
        self.history_manager = history_manager
        self.timeframes = timeframes or ['1min','5min','15min','1h','4h']
        self.data = {}  # armazena candles multitimeframe
        self.features = {}  # indicadores calculados

    def load_candles(self):
        """Carrega candles históricos para cada timeframe"""
        for tf in self.timeframes:
            candles = self.history_manager.get_candles(tf)
            if candles is not None and not candles.empty:
                self.data[tf] = candles.copy()
            else:
                self.data[tf] = pd.DataFrame()

    def calculate_indicators(self):
        """Calcula indicadores para cada timeframe (retrovisor)"""
        for tf, df in self.data.items():
            if df.empty:
                continue

            # Retorno logarítmico
            df['log_ret'] = np.log(df['close']/df['close'].shift(1))
            # Média móvel simples e exponencial
            df['sma_20'] = df['close'].rolling(20).mean()
            df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
            # ATR (Average True Range)
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift(1))
            low_close = np.abs(df['low'] - df['close'].shift(1))
            df['tr'] = high_low.combine(high_close, max).combine(low_close, max)
            df['atr_14'] = df['tr'].rolling(14).mean()
            # Momentum
            df['momentum'] = df['close'] - df['close'].shift(10)
            # Desvio padrão (volatilidade)
            df['std'] = df['log_ret'].rolling(20).std()
            # Z-score
            df['zscore'] = (df['close'] - df['sma_20']) / df['std']

            # Armazena indicadores
            self.features[tf] = df

    def get_features_for_core(self):
        """Retorna os principais indicadores para alimentar o motor central"""
        core_features = {}
        for tf, df in self.features.items():
            if df.empty:
                continue
            core_features[tf] = {
                'close': df['close'].iloc[-1],
                'sma_20': df['sma_20'].iloc[-1],
                'ema_20': df['ema_20'].iloc[-1],
                'atr_14': df['atr_14'].iloc[-1],
                'momentum': df['momentum'].iloc[-1],
                'zscore': df['zscore'].iloc[-1]
            }
        return core_features

    def update(self):
        """Atualiza dados e indicadores"""
        self.load_candles()
        self.calculate_indicators()
        return self.get_features_for_core()

# Exemplo de uso:
# market_state = MarketState(history_manager)
# features = market_state.update()
# features agora contém indicadores multitimeframe para alimentar o motor central

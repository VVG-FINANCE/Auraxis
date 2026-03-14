# engine/candle_analysis.py
# Responsável por analisar candles, detectar padrões, gerar oportunidades
# e criar zonas de entrada, integrando informações do retrovisor multitimeframe

import pandas as pd
import numpy as np

class CandleAnalysis:
    def __init__(self, market_features, history_manager):
        """
        market_features: dict de features multitimeframe do módulo MarketState
        history_manager: objeto que gerencia histórico em SQLite
        """
        self.market_features = market_features
        self.history_manager = history_manager
        self.opportunities = []

    def detect_patterns(self, tf='1min'):
        """
        Detecta padrões clássicos de candles e confirma com retrovisor multitimeframe
        """
        df = self.history_manager.get_candles(tf)
        if df is None or df.empty:
            return []

        patterns = []

        # Exemplo simples: Engolfo de alta e baixa
        for i in range(1, len(df)):
            prev = df.iloc[i-1]
            curr = df.iloc[i]
            # Engolfo de alta
            if curr['close'] > curr['open'] and prev['close'] < prev['open'] and curr['open'] < prev['close'] and curr['close'] > prev['open']:
                patterns.append({'index': i, 'type': 'bull_engulfing'})
            # Engolfo de baixa
            elif curr['close'] < curr['open'] and prev['close'] > prev['open'] and curr['open'] > prev['close'] and curr['close'] < prev['open']:
                patterns.append({'index': i, 'type': 'bear_engulfing'})

        return patterns

    def generate_zones(self, tf='1min'):
        """
        Gera zonas de suporte e resistência com base em retrovisor multitimeframe
        """
        df = self.history_manager.get_candles(tf)
        if df is None or df.empty:
            return []

        # Suportes e resistências simples: máximos e mínimos dos últimos N candles
        N = 20
        zones = []
        highs = df['high'].rolling(N).max()
        lows = df['low'].rolling(N).min()

        for i in range(N, len(df)):
            zone = {
                'upper': highs.iloc[i],
                'lower': lows.iloc[i],
                'timeframe': tf
            }
            zones.append(zone)

        return zones

    def evaluate_opportunities(self):
        """
        Cria oportunidades de entrada combinando padrões e zonas
        """
        self.opportunities = []
        for tf in self.market_features.keys():
            patterns = self.detect_patterns(tf)
            zones = self.generate_zones(tf)

            for pat in patterns:
                # Seleciona zona mais próxima do candle
                candle_index = pat['index']
                if zones:
                    zone = zones[min(candle_index - len(zones) + 1, len(zones)-1)]
                else:
                    zone = None

                # Score inicial baseado em tipo de padrão (pode ser ajustado por Bayes e Monte Carlo depois)
                score = 50
                if pat['type'] == 'bull_engulfing':
                    score += 10
                elif pat['type'] == 'bear_engulfing':
                    score -= 10

                opportunity = {
                    'timeframe': tf,
                    'candle_index': candle_index,
                    'pattern': pat['type'],
                    'zone': zone,
                    'score': score,
                    'sl': None,  # Stop Loss a ser definido pelo motor central
                    'tp': None   # Take Profit a ser definido pelo motor central
                }

                self.opportunities.append(opportunity)

        return self.opportunities

    def update(self):
        """
        Atualiza oportunidades com base em novos candles e retrovisor multitimeframe
        """
        self.evaluate_opportunities()
        return self.opportunities

# Exemplo de uso:
# candle_analysis = CandleAnalysis(market_features, history_manager)
# opportunities = candle_analysis.update()
# opportunities contém todas as entradas candidatas com padrões e zonas

# engine/monte_carlo.py
# Motor de simulação Monte Carlo para previsão de preço e ajuste probabilístico do score

import numpy as np
import pandas as pd

class MonteCarloEngine:
    def __init__(self, history_manager, n_simulations=1000, horizon=10):
        """
        history_manager: objeto HistoryManager
        n_simulations: número de trajetórias Monte Carlo
        horizon: número de passos futuros (ex: minutos)
        """
        self.history_manager = history_manager
        self.n_simulations = n_simulations
        self.horizon = horizon

    def simulate_price_paths(self, timeframe='1min'):
        """
        Simula trajetórias futuras de preço usando retorno logarítmico
        """
        df = self.history_manager.get_candles(timeframe)
        if df is None or df.empty:
            return None

        log_ret = np.log(df['close'] / df['close'].shift(1)).dropna()
        mu = log_ret.mean()
        sigma = log_ret.std()

        S0 = df['close'].iloc[-1]

        simulations = np.zeros((self.n_simulations, self.horizon))
        for i in range(self.n_simulations):
            prices = [S0]
            for t in range(1, self.horizon):
                dt = 1
                shock = np.random.normal(mu*dt, sigma*np.sqrt(dt))
                price_t = prices[-1] * np.exp(shock)
                prices.append(price_t)
            simulations[i] = prices

        return simulations

    def simulate(self, opportunity):
        """
        Ajusta o score de uma oportunidade baseado na simulação Monte Carlo
        """
        tf = opportunity.get('timeframe', '1min')
        simulations = self.simulate_price_paths(tf)
        if simulations is None:
            return 0

        tp = opportunity.get('tp')
        sl = opportunity.get('sl')
        if tp is None or sl is None:
            # Sem TP/SL definidos ainda
            tp = simulations[:, -1].mean() * 1.002
            sl = simulations[:, -1].mean() * 0.998

        # Probabilidade de atingir TP antes de SL
        hits_tp = (simulations[:, -1] >= tp).sum()
        hits_sl = (simulations[:, -1] <= sl).sum()
        prob = hits_tp / max(hits_tp + hits_sl, 1)

        # Ajuste de score proporcional à probabilidade
        score_adjustment = (prob - 0.5) * 20  # +10 se 75% chance, -10 se 25%
        return score_adjustment

# Exemplo de uso:
# monte_carlo = MonteCarloEngine(history_manager)
# mc_adjustment = monte_carlo.simulate(opportunity)

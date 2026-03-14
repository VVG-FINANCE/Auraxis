# engine/core.py
# Motor central do sistema
# Integra retrovisor multitimeframe, análise de candles, ML, Monte Carlo, Bayes e score final

import numpy as np
from engine.market_state import MarketState
from engine.candle_analysis import CandleAnalysis
from engine.ml_module import MLModule
from engine.monte_carlo import MonteCarloEngine
from engine.bayes import BayesEngine

class CoreEngine:
    def __init__(self, history_manager):
        self.history_manager = history_manager

        # Motores integrados
        self.market_state = MarketState(history_manager)
        self.ml_module = MLModule(history_manager)
        self.candle_analysis = None  # Inicializado após retrovisor
        self.monte_carlo = MonteCarloEngine(history_manager)
        self.bayes = BayesEngine(history_manager)

        # Lista de oportunidades finais
        self.opportunities = []

    def update_market(self):
        """
        Atualiza o retrovisor multitimeframe
        """
        market_features = self.market_state.update()
        return market_features

    def analyze_candles(self, market_features):
        """
        Atualiza análise de candles e gera oportunidades iniciais
        """
        self.candle_analysis = CandleAnalysis(market_features, self.history_manager)
        opportunities = self.candle_analysis.update()
        return opportunities

    def adjust_score_ml(self, market_features, opportunities):
        """
        Ajusta o score de cada oportunidade usando ML e retrovisor
        """
        features_df = self.ml_module.integrate_retrovisor(market_features)

        # Se não houver oportunidades ou features, mantém score inicial
        if features_df.empty:
            return opportunities

        # Predição de score via ML
        predicted_scores = self.ml_module.predict_score(features_df)
        for i, opp in enumerate(opportunities):
            if i < len(predicted_scores):
                opp['score'] = predicted_scores[i]
        return opportunities

    def adjust_score_monte_carlo(self, opportunities):
        """
        Refina o score usando simulação Monte Carlo
        """
        for opp in opportunities:
            mc_adjustment = self.monte_carlo.simulate(opp)
            opp['score'] = np.clip(opp['score'] + mc_adjustment, 0, 100)
        return opportunities

    def adjust_score_bayes(self, opportunities):
        """
        Refina o score usando probabilidade Bayesiana
        """
        for opp in opportunities:
            bayes_adjustment = self.bayes.update_probability(opp)
            opp['score'] = np.clip(opp['score'] + bayes_adjustment, 0, 100)
        return opportunities

    def finalize_opportunities(self, opportunities):
        """
        Calcula SL/TP e risk/reward baseado em zona, retrovisor e score
        """
        for opp in opportunities:
            zone = opp.get('zone')
            close_price = zone['upper'] if zone else 1.0
            atr = 0.0010  # placeholder, pode pegar de market_state
            opp['sl'] = close_price - 2 * atr
            opp['tp'] = close_price + 2 * atr
        return opportunities

    def run_cycle(self):
        """
        Executa o ciclo completo do motor central
        """
        # 1. Atualiza retrovisor multitimeframe
        market_features = self.update_market()

        # 2. Analisa candles e gera oportunidades iniciais
        opportunities = self.analyze_candles(market_features)

        # 3. Ajusta score via ML
        opportunities = self.adjust_score_ml(market_features, opportunities)

        # 4. Ajusta score via Monte Carlo
        opportunities = self.adjust_score_monte_carlo(opportunities)

        # 5. Ajusta score via Bayes
        opportunities = self.adjust_score_bayes(opportunities)

        # 6. Calcula SL/TP e risk/reward final
        self.opportunities = self.finalize_opportunities(opportunities)

        return self.opportunities

# Exemplo de uso:
# core_engine = CoreEngine(history_manager)
# final_opps = core_engine.run_cycle()
# final_opps agora contém entradas com score final, SL/TP e zone

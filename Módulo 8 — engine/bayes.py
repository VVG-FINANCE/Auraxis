# engine/bayes.py
# Motor de estatística Bayesiana para ajuste probabilístico do score
# Integra retrovisor, Monte Carlo e ML

import numpy as np

class BayesEngine:
    def __init__(self, history_manager):
        """
        history_manager: objeto HistoryManager
        """
        self.history_manager = history_manager
        self.prior_success_rate = 0.5  # prior inicial: 50%
        self.alpha = 1  # parâmetro beta para posterior
        self.beta = 1

    def update_probability(self, opportunity):
        """
        Atualiza score baseado na probabilidade Bayesiana de sucesso
        """
        # Obtém histórico de sucesso do ativo (simulado ou real)
        # Para simplificação: usa prior + ajuste do Monte Carlo ou ML
        score = opportunity.get('score', 50)
        mc_adjustment = opportunity.get('mc_adjustment', 0)
        ml_adjustment = opportunity.get('ml_adjustment', 0)

        # Atualiza beta-binomial posterior
        successes = self.alpha + max(score + mc_adjustment + ml_adjustment, 0) / 100
        failures = self.beta + max(100 - score - mc_adjustment - ml_adjustment, 0) / 100
        posterior = successes / (successes + failures)

        # Ajuste de score: de -10 a +10 proporcional à diferença do prior
        score_adjustment = (posterior - self.prior_success_rate) * 20

        return score_adjustment

# Exemplo de uso:
# bayes_engine = BayesEngine(history_manager)
# bayes_adjustment = bayes_engine.update_probability(opportunity)

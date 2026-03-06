# =========================
# monte_carlo.py - Auraxis robusto
# =========================
import numpy as np

class MonteCarlo:
    """
    Simulação de Monte Carlo para prever cenários de preço EUR/USD
    """

    def __init__(self, n_simulations=1000):
        self.n_simulations = n_simulations

    def simular_preco(self, preco_atual, volatilidade=0.001, passos=10):
        """
        Simula caminhos futuros de preço usando Monte Carlo
        :param preco_atual: preço base
        :param volatilidade: variação percentual média por passo
        :param passos: número de passos futuros
        :return: lista de arrays com simulações
        """
        resultados = []
        for _ in range(self.n_simulations):
            precos = [preco_atual]
            for _ in range(passos):
                movimento = np.random.normal(0, volatilidade)
                preco_novo = precos[-1] * (1 + movimento)
                precos.append(preco_novo)
            resultados.append(precos)
        return np.array(resultados)

    def calcular_probabilidade_alcance(self, simulacoes, nivel):
        """
        Calcula probabilidade de atingir determinado nível de preço
        """
        count = np.sum(simulacoes >= nivel)
        total = simulacoes.size
        return round(count / total, 4)

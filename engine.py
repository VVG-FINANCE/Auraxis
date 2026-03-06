# =========================
# engine.py - Auraxis robusto
# =========================
from data_manager import DataManager
from candle_analysis import CandleAnalysis
from machine_learning import MLModule
from datetime import datetime

class Engine:
    """
    Motor interno do Auraxis
    - Integra dados reais, candle analysis e ML
    - Gera oportunidades, mantém histórico e score
    """

    def __init__(self):
        self.data_manager = DataManager()
        self.candle_analysis = CandleAnalysis()
        self.ml_module = MLModule()
        self.oportunidades = []

    # =========================
    # Atualiza candles e treina ML
    # =========================
    def atualizar_candles(self, n=100):
        candles = self.data_manager.obter_candles(n)
        # Labels fictícias para treino inicial (1=Compra, 0=Venda)
        labels = [1 if i % 2 == 0 else 0 for i in range(len(candles))]
        self.ml_module.treinar(candles, labels)
        return candles

    # =========================
    # Gera oportunidade baseada no candle atual
    # =========================
    def gerar_oportunidade(self):
        candles = self.data_manager.obter_candles(2)
        candle_atual = candles[-1]
        candle_anterior = candles[-2]

        # CandleAnalysis gera oportunidade básica
        opp = self.candle_analysis.gerar_oportunidade(candle_atual)
        if not opp:
            return None

        # ML ajusta score
        ml_score = self.ml_module.predizer(candle_atual, candle_anterior, score_base=opp["score"])
        opp["score"] = ml_score

        # Salva oportunidade
        self.oportunidades.append(opp)
        if len(self.oportunidades) > 50:
            self.oportunidades.pop(0)
        return opp

    # =========================
    # Retorna oportunidades recentes
    # =========================
    def obter_oportunidades(self, n=10):
        return self.oportunidades[-n:]

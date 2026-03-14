# engine/ml_module.py
# Responsável pelo ajuste do score usando ML, regime HMM e feature importance
# Integra dados do retrovisor multitimeframe e motores analíticos

import numpy as np
import pandas as pd
from hmmlearn import hmm
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

class MLModule:
    def __init__(self, history_manager):
        """
        history_manager: objeto que fornece histórico de candles e features
        """
        self.history_manager = history_manager
        self.model = None
        self.scaler = StandardScaler()
        self.hmm_model = None
        self.feature_importance = {}

    def train_hmm_regime(self, timeframe='1min', n_states=3):
        """
        Treina HMM para identificar regimes de mercado
        """
        df = self.history_manager.get_candles(timeframe)
        if df is None or df.empty:
            return None

        # Usando retorno logarítmico e volatilidade
        X = df[['close']].pct_change().dropna().values
        self.hmm_model = hmm.GaussianHMM(n_components=n_states, covariance_type="full", n_iter=100)
        self.hmm_model.fit(X)
        df['regime'] = self.hmm_model.predict(X)
        return df['regime']

    def train_score_model(self, features_df, target):
        """
        Treina um modelo de ML para ajustar score
        features_df: dataframe de features multitimeframe
        target: score alvo (0-100)
        """
        if features_df.empty or len(features_df) != len(target):
            return None

        X_scaled = self.scaler.fit_transform(features_df)
        self.model = RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42)
        self.model.fit(X_scaled, target)

        # Armazena importância das features
        self.feature_importance = dict(zip(features_df.columns, self.model.feature_importances_))
        return self.model

    def predict_score(self, features_df):
        """
        Ajusta o score para novas oportunidades usando ML
        """
        if self.model is None or features_df.empty:
            return None

        X_scaled = self.scaler.transform(features_df)
        scores = self.model.predict(X_scaled)
        # Normaliza para 0-100
        scores = np.clip(scores, 0, 100)
        return scores

    def integrate_retrovisor(self, market_features):
        """
        Integra múltiplos timeframes (retrovisor) como input para ML
        """
        # Exemplo: concatena features de todos timeframes
        df_list = []
        for tf, feats in market_features.items():
            feats_flat = {f"{tf}_{k}": v for k, v in feats.items()}
            df_list.append(pd.DataFrame([feats_flat]))
        if df_list:
            return pd.concat(df_list, axis=1)
        else:
            return pd.DataFrame()

# Exemplo de uso:
# ml_module = MLModule(history_manager)
# regimes = ml_module.train_hmm_regime('1min')
# features_df = ml_module.integrate_retrovisor(market_features)
# ml_module.train_score_model(features_df, target_score)
# adjusted_scores = ml_module.predict_score(features_df)

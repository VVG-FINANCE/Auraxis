# config.py
# Parâmetros de configuração do sistema de trading EUR/USD

# -------------------------
# Trading Parameters
# -------------------------
TRADING_TIMEFRAMES = ['1min', '5min', '15min', '1h', '4h']  # Retrovisor multitimeframe
DEFAULT_PIP_ADJUSTMENT = 0.0   # Ajuste manual em pips (ex: 30 pips = 0.0030)
ATR_MULTIPLIER_SL = 2          # Multiplicador do ATR para Stop Loss
ATR_MULTIPLIER_TP = 2          # Multiplicador do ATR para Take Profit
MAX_SCORE = 100
MIN_SCORE = 0

# -------------------------
# Monte Carlo Parameters
# -------------------------
MC_SIMULATIONS = 1000          # Número de trajetórias
MC_HORIZON = 10                # Passos futuros (minutos)

# -------------------------
# Bayes Parameters
# -------------------------
BAYES_PRIOR = 0.5              # Probabilidade inicial de sucesso
BAYES_ALPHA = 1                # Parâmetro beta-binomial
BAYES_BETA = 1

# -------------------------
# ML Parameters
# -------------------------
ML_N_ESTIMATORS = 200
ML_MAX_DEPTH = 6
ML_RANDOM_STATE = 42

# -------------------------
# Data Sources and API Keys
# -------------------------
EXCHANGE_RATE_API_URL = "https://api.exchangerate.host/latest?base=EUR&symbols=USD"
FRANKFURTER_API_URL = "https://api.frankfurter.app/latest?from=EUR&to=USD"
YFINANCE_TICKER = "EURUSD=X"

# -------------------------
# Fallback Intervals (segundos)
# -------------------------
FALLBACK_INTERVALS = [5, 10, 15, 30, 60]  # Progressivo em caso de falha na coleta de dados

# -------------------------
# UI / Flask
# -------------------------
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
FLASK_DEBUG = True

# -------------------------
# SQLite / Database
# -------------------------
DATABASE_PATH = 'data/market.db'

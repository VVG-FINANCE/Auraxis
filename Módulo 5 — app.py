# app.py
# Web App Flask para mobile, integrando CoreEngine e exibindo oportunidades

from flask import Flask, render_template
from engine.core import CoreEngine
from data_pipeline.history_manager import HistoryManager

# Inicialização do Flask
app = Flask(__name__)

# Inicializa history manager e motor central
history_manager = HistoryManager('data/market.db')
core_engine = CoreEngine(history_manager)

@app.route('/')
def index():
    # Executa ciclo do motor central
    opportunities = core_engine.run_cycle()

    # Ajusta visualização: arredonda preços e score
    for opp in opportunities:
        opp['score'] = round(opp['score'], 2)
        opp['sl'] = round(opp['sl'], 5)
        opp['tp'] = round(opp['tp'], 5)
        if opp.get('zone'):
            opp['zone']['upper'] = round(opp['zone']['upper'], 5)
            opp['zone']['lower'] = round(opp['zone']['lower'], 5)

    # Renderiza template
    return render_template('index.html', opportunities=opportunities)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

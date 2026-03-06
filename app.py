# =========================
# app.py - Auraxis robusto
# =========================
import flet as ft
from engine import Engine
from config import UI_CONFIG

class AuraxisApp:
    """
    Interface mobile do Auraxis usando Flet
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.engine = Engine()
        self.page.title = "Auraxis - Simulador EUR/USD"
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.bgcolor = UI_CONFIG["cores"]["background"]

        # Abas
        self.tabs = ft.Tabs(
            tabs=[
                ft.Tab(text="Mercado", content=ft.Column(), icon=ft.icons.SHOW_CHART),
                ft.Tab(text="Oportunidades", content=ft.Column(), icon=ft.icons.TRADING),
                ft.Tab(text="Histórico", content=ft.Column(), icon=ft.icons.HISTORY),
            ],
            expand=True
        )

        self.page.add(self.tabs)
        self.atualizar_interface()

    # =========================
    # Atualiza interface
    # =========================
    def atualizar_interface(self):
        # Atualiza candles
        self.engine.atualizar_candles()
        opp = self.engine.gerar_oportunidade()

        # ---------- Aba Mercado ----------
        mercado_col = self.tabs.tabs[0].content
        mercado_col.controls.clear()
        preco = self.engine.data_manager.obter_preco_atual()
        mercado_col.controls.append(ft.Text(f"Preço EUR/USD: {preco:.5f}", size=24, color=UI_CONFIG["cores"]["entrada"]))

        # Últimos 5 candles
        candles = self.engine.data_manager.obter_candles(5)
        for c in candles:
            mercado_col.controls.append(ft.Text(f"{c['time']} | O:{c['open']} H:{c['high']} L:{c['low']} C:{c['close']}", size=16, color=UI_CONFIG["cores"]["texto"]))

        # ---------- Aba Oportunidades ----------
        opp_col = self.tabs.tabs[1].content
        opp_col.controls.clear()
        if opp:
            cor_tipo = UI_CONFIG["cores"]["positivo"] if opp["tipo"]=="Compra" else UI_CONFIG["cores"]["negativo"]
            opp_col.controls.append(ft.Text(f"Oportunidade: {opp['tipo']} | Score: {opp['score']} | RR: {opp['rr']}", size=20, color=cor_tipo))
            opp_col.controls.append(ft.Text(f"Entrada Ext: {opp['entrada_externa']} | Entrada Int: {opp['entrada_interna']}", size=16, color=UI_CONFIG["cores"]["entrada"]))
            opp_col.controls.append(ft.Text(f"Stop: {opp['stop']} | Take: {opp['take']} | Tendência: {opp['tendencia']}", size=16, color=UI_CONFIG["cores"]["stop"]))
        else:
            opp_col.controls.append(ft.Text("Nenhuma oportunidade no momento.", size=16, color=UI_CONFIG["cores"]["texto"]))

        # ---------- Aba Histórico ----------
        hist_col = self.tabs.tabs[2].content
        hist_col.controls.clear()
        for o in self.engine.obter_oportunidades(10)[::-1]:
            cor_tipo = UI_CONFIG["cores"]["positivo"] if o["tipo"]=="Compra" else UI_CONFIG["cores"]["negativo"]
            hist_col.controls.append(ft.Text(f"{o['time']} | {o['tipo']} | Score: {o['score']} | RR: {o['rr']}", size=16, color=cor_tipo))

        # Atualiza página
        self.page.update()

        # Atualiza novamente em 5 segundos
        self.page.timer(TRADING_CONFIG["fragmentacao_segundos"], self.atualizar_interface)

def main(page: ft.Page):
    AuraxisApp(page)

ft.app(target=main, view=ft.WEB_BROWSER)

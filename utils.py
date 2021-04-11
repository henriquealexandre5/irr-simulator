import numpy as np
import plotly.graph_objects as go
import streamlit as st
import numpy_financial as npf


def waterfall_plot(cashflow, label=""):
    n = cashflow.shape[0]
    fig = go.Figure(
        go.Waterfall(
            name="",
            orientation="v",
            measure=["absolute"] * n,
            x=["Mês " + str(x) for x in range(n)],
            textposition="outside",
            y=cashflow,
            connector={"line": {"width": 0,"color": "black"}},
            totals = {"marker":{"color":"#ff774a", "line":{"color":"black", "width":1}}}
        )
    )
    fig.update_layout(
        title={"text": label, "x": 0.5, "xanchor": "center"}, showlegend=False,
    )
    
    # fig.update_layout({
    #     'plot_bgcolor': 'white',
    #     'paper_bgcolor': 'white',
    #     })
    
    st.plotly_chart(fig)


class UnitCashflow:
    def __init__(self, params, len_cashflow=25):
        self.params = params
        self.flows = [
            "buying_cashflow",
            "holding_costs_cashflow",
            "renovation_costs_cashflow",
            "selling_cashflow",
        ]
        self.init_cashflows(cashflow_size=len_cashflow)
        self.consolidate_cashflows()

    def init_cashflows(self, cashflow_size):
        # Cashflow Total
        self.cashflow = np.zeros(cashflow_size)
        # Cashflow por fluxo
        self.cashflows = {}
        for flow in self.flows:
            self.cashflows[flow] = np.zeros(cashflow_size)

    def buying_cashflow(self):
        # Pagamento do sinal em T = 0
        self.cashflows["buying_cashflow"][0] = (
            -self.params["downpayment"] * self.params["buying_price"]
        )
        # Pagamento do valor restante em T = 1
        self.cashflows["buying_cashflow"][1] = (
            -(1 - self.params["downpayment"]) * self.params["buying_price"]
        )

    def holding_costs_cashflow(self):
        # Holding costs começa em T = 1 até T = HP - 1
        # (começa a ser pago no momento da escritura de compra e vai até um mês antes da escritura de venda)
        self.cashflows["holding_costs_cashflow"][1 : self.params["holding_period"]] -= (
            self.params["community_fee"] + self.params["property_tax"]
        )

    def renovation_costs_cashflow(self):
        # Reforma começa em T = 1 e vai até T = 1 + renovation_time
        renovation_start = 1
        renovation_end = renovation_start + self.params["renovation_time"]
        # Valor da reforma é distribuido igualmente entre o tempo
        self.cashflows["renovation_costs_cashflow"][
            renovation_start:renovation_end
        ] = -self.params["renovation_cost"] / max(self.params["renovation_time"], 1)

    def selling_cashflow(self):
        # Recebimento do sinal em T = HP - 1
        self.cashflows["selling_cashflow"][self.params["holding_period"] - 1] = (
            self.params["downpayment"] * self.params["selling_price"]
        )
        # Recebimento do valor restante em T = HP
        self.cashflows["selling_cashflow"][self.params["holding_period"]] = (
            1 - self.params["downpayment"]
        ) * self.params["selling_price"]

    def consolidate_cashflows(self):
        self.buying_cashflow()
        self.holding_costs_cashflow()
        self.renovation_costs_cashflow()
        self.selling_cashflow()

        for flow in self.flows:
            self.cashflow += self.cashflows[flow]

    def get_irr(self):
        return ((1 + npf.irr(self.cashflow)) ** (12) - 1) * 100

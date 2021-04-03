import streamlit as st
from utils import UnitCashflow, waterfall_plot

_, col_image, _ = st.beta_columns([1,1,1])
col_image.image("loft_logo.png")

#Título calculadora
st.markdown(
    "<h1 style='text-align: center; color: #ff774a;'>Calculadora de TIR</h1>",
    unsafe_allow_html=True,
)

#Informações
file = """
<details>
<summary>ℹ️ Informação</summary>

- Para realizar os cálculos de TIR assumimos algumas premissas:
    - Registro da escritura de compra acontece 1 mês após assinatura do contrato de compra
    - Reforma começa imediatamente após a assinatura da escritura de compra
    - Valor da reforma é distribuido igualmente entre os meses
    - Escritura de venda é registrada 1 mês após a assinatura do contrato com o comprador
    - No momento da assinatura dos contratos de compra e venda é pago e recebido, respectivamente, um sinal de 10%
- ** Quer ter uma experiência personalizada? Vem falar com a gente! ** :orange_heart:

</details>
"""
st.markdown(file,unsafe_allow_html=True)
st.write("\n")

#Inputs usados na calculadora (Texto, Valor mínimo, Valor máximo, Valor inicial)
inputs = {"renovation_time": ("Tempo de reforma", 0, 12, 0),
          "renovation_cost": ("Valor da reforma", 0, 10 ** 6, 0),
          "community_fee": ("Condomínio", 0, 10 ** 5, 0),
          "property_tax": ("IPTU", 0, 10 ** 5, 0),
          "holding_period": ("Holding period (tempo entre as escrituras de compra e venda)", 0, 16, 0),
          "selling_price": ("Valor de venda", 0, 10 ** 8, 0),
          "buying_price": ("Valor de compra", 0, 10 ** 8, 0),
}

#Fazer campos lado a lado
cols = {'renovation_time': 'col1',
        'renovation_cost': 'col2',
        'community_fee': 'col3',
        'property_tax': 'col4'}

col1, col2 = st.beta_columns(2)
col3, col4 = st.beta_columns(2)

for var, values in inputs.items():
    if var in cols:
        inputs[var] = eval(f'{cols[var]}.number_input' + str(values))
    else:    
        inputs[var] = eval('st.number_input' + str(values)) 

#Resultados
cashflow_size = 25
inputs['downpayment'] = 0.1

ap = UnitCashflow(inputs, len_cashflow = cashflow_size)

st.subheader("TIR (% a.a)")
if (inputs["buying_price"] == 0) | (inputs["selling_price"] == 0) | (inputs["holding_period"] == 0):
    st.write('Adicione todos os valores para realizar o cálculo')
else:
    st.write(round(ap.get_irr(), 2))

st.write('----')

##Mostrar cashflows

#Total
waterfall_plot(ap.cashflow, "Cashflow total")

# Buy
with st.beta_expander("Cashflow de compra"):
    waterfall_plot(ap.cashflows['buying_cashflow'])

# Holding costs
with st.beta_expander("Cashflow de holding costs"):
    waterfall_plot(ap.cashflows['holding_costs_cashflow'])

# Renovations
with st.beta_expander("Cashflow de reforma"):
    waterfall_plot(ap.cashflows['renovation_costs_cashflow'])

# Sell
with st.beta_expander("Cashflow de venda"):
    waterfall_plot(ap.cashflows['selling_cashflow'])

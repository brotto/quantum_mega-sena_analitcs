import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def exibir_evolucao_raizes(predictor):
    if not predictor.numeros_raizes or len(predictor.numeros_raizes) == 0:
        st.warning("Não há números raízes suficientes para exibir o gráfico.")
        return

    st.subheader("Evolução dos Números Raízes ao Longo do Tempo")

    janelas = [r['janela_idx'] for r in predictor.numeros_raizes]
    n_raizes = len(predictor.numeros_raizes[0]['raizes'])
    cores = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", "#19D3F3"]

    fig = go.Figure()

    for i in range(n_raizes):
        valores = [r['raizes'][i] if i < len(r['raizes']) else None for r in predictor.numeros_raizes]
        fig.add_trace(go.Scatter(
            x=janelas,
            y=valores,
            mode='lines+markers',
            name=f"Raiz {i+1}",
            line=dict(color=cores[i % len(cores)])
        ))

    for ponto in predictor.pontos_mudanca:
        fig.add_vline(x=ponto['janela_idx'], line=dict(color='black', dash='dash'),
                      annotation_text="Mudança", annotation_position="top")

    st.plotly_chart(fig, use_container_width=True)

    st.info("As linhas verticais tracejadas indicam momentos de mudança nos números raízes, que podem sinalizar o fim de um período de estabilidade. Estratégias preditivas baseadas em raízes são mais eficazes dentro de períodos estáveis.")

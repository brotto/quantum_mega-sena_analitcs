import streamlit as st
from mega_sena_predictor import MegaSenaPredictor
from raizes_grafico_streamlit import exibir_evolucao_raizes
import os

# Inicializar o sistema
predictor = MegaSenaPredictor()

st.set_page_config(page_title="Quantum Mega Sena", layout="wide")
st.title("🔮 Quantum Mega Sena Analytics")
st.markdown("Explore padrões ocultos nos resultados da Mega Sena com análise estatística e simulação quântica.")

# Sidebar
st.sidebar.header("Configurações")

janela = st.sidebar.slider("Tamanho da janela de análise", min_value=10, max_value=100, value=50)
n_raizes = st.sidebar.slider("Quantidade de números raízes", min_value=1, max_value=6, value=3)
n_qubits = st.sidebar.slider("Qubits para simulação quântica", min_value=3, max_value=8, value=6)

# Botões de ação
if st.sidebar.button("🔁 Carregar dados"):
    if predictor.carregar_dados():
        st.success(f"Dados carregados: {len(predictor.sorteios)} sorteios.")
    else:
        st.error("Erro ao carregar dados.")

if st.sidebar.button("🔍 Detectar números raízes"):
    predictor.detectar_numeros_raizes(tamanho_janela=janela, n_raizes=n_raizes)
    st.success("Números raízes detectados.")
    exibir_evolucao_raizes(predictor)

if st.sidebar.button("📈 Detectar períodos de estabilidade"):
    predictor.detectar_periodos_estabilidade()
    st.image(os.path.join(predictor.output_dir, "periodos_estabilidade.png"))
    st.success("Períodos detectados.")

    periodo_atual = predictor.periodos_estaveis[-1] if predictor.periodos_estaveis else None

    if periodo_atual:
        st.markdown("### 🔍 Análise do Período Atual")
        st.markdown(f"O período atual começou no sorteio **{periodo_atual['inicio']}** e já dura **{periodo_atual['tamanho']}** sorteios.")
        if periodo_atual['tamanho'] >= 10:
            st.success("Este é um período estável relativamente longo. Pode ser um bom momento para aplicar estratégias baseadas em números raízes.")
        else:
            st.warning("O período atual é recente. Estratégias baseadas em estabilidade podem ter desempenho incerto neste momento.")
    else:
        st.info("Não foi possível identificar um período atual de estabilidade.")

if st.sidebar.button("⚛️ Simulação quântica"):
    result = predictor.simular_computacao_quantica(n_qubits=n_qubits)
    if result:
        st.image(os.path.join(predictor.output_dir, "resultados_quanticos.png"), caption="Resultados Quânticos")
        st.image(os.path.join(predictor.output_dir, "numeros_quanticos.png"), caption="Números Previstos")
        st.success(f"Números previstos: {result['numeros_previstos']}")

if st.sidebar.button("🎯 Gerar previsões"):
    previsoes = predictor.gerar_previsoes()
    st.image(os.path.join(predictor.output_dir, "previsoes_finais.png"))
    st.markdown("### Previsões:")
    for p in previsoes:
        st.markdown(f"- **{p['metodo']}**: {p['numeros']} (Confiança: {p['confianca']:.2f})")

if st.sidebar.button("🧪 Validar previsão do 101º sorteio"):
    resultado = predictor.validar_previsao_101()
    if resultado:
        st.markdown(f"### Validação do sorteio {resultado['sorteio_previsto']}")
        st.markdown(f"**Números reais:** {resultado['numeros_reais']}")
        for p in resultado["previsoes"]:
            st.markdown(f"- **{p['metodo']}**: {p['numeros']} – Acertos: {p['acertos']}/6")
        st.markdown(f"**Média de acertos:** {resultado['media_acertos']:.2f}/6")

st.markdown("---")
st.caption("Desenvolvido por Brotto — com análise estatística, teoria dos jogos e inspiração quântica.")
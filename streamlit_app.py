import streamlit as st
from mega_sena_predictor import MegaSenaPredictor
from raizes_grafico_streamlit import exibir_evolucao_raizes
import os
from interprete_ia import interpretar_estabilidade_via_ia

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

    periodo_atual = predictor.periodos_estabilidade[-1] if predictor.periodos_estabilidade else None

    if periodo_atual:
        st.markdown("### 🔍 Análise do Período Atual")
        st.markdown(f"O período atual começou no sorteio **{periodo_atual['inicio']}** e já dura **{periodo_atual['tamanho']}** sorteios.")
        if periodo_atual['tamanho'] >= 10:
            st.success("Este é um período estável relativamente longo. Pode ser um bom momento para aplicar estratégias baseadas em números raízes.")
        else:
            st.warning("O período atual é recente. Estratégias baseadas em estabilidade podem ter desempenho incerto neste momento.")
        
        st.markdown("### 🧠 Sugestão Estratégica")
        if periodo_atual['tamanho'] >= 15:
            st.markdown("- Estratégia sugerida: **utilizar os números raízes atuais como base principal para seus jogos**.\n- Considere repetir combinações com variações mínimas.")
        elif periodo_atual['tamanho'] >= 10:
            st.markdown("- Estratégia sugerida: **usar os números raízes como âncora**, combinando com dezenas mais frequentes ou pares históricos.")
        else:
            st.markdown("- Estratégia sugerida: **aguardar mais sorteios ou diversificar jogos**, pois o padrão ainda está se formando.")
        
        st.markdown("### ✅ Ação Ideal no Período Atual")
        if periodo_atual['tamanho'] >= 15:
            st.success("🟢 Recomendação: Aplicar estratégias agressivas baseadas em raízes — como fixar 3 a 4 dezenas raízes por jogo.")
        elif periodo_atual['tamanho'] >= 10:
            st.info("🟡 Recomendação: Combinar raízes com padrões históricos — estratégia de equilíbrio.")
        else:
            st.warning("🔴 Recomendação: Aguardar ou variar suas apostas enquanto o padrão se estabiliza.")
        
        # Interpretação por IA com base no período atual
        interpretacao = interpretar_estabilidade_via_ia(periodo_atual, len(predictor.periodos_estabilidade))
        st.markdown("### 🤖 Interpretação da IA")
        st.markdown(interpretacao)
    else:
        st.info("Não foi possível identificar um período atual de estabilidade.")

        # Chamar IA mesmo sem período atual
        interpretacao = interpretar_estabilidade_via_ia(None, len(predictor.periodos_estabilidade))
        st.markdown("### 🤖 Interpretação da IA")
        st.markdown(interpretacao)

if st.sidebar.button("⚛️ Simulação quântica"):
    if not predictor.sorteios or len(predictor.sorteios) < 20:
        st.warning("Simulação indisponível: são necessários pelo menos 20 sorteios carregados para rodar a simulação quântica.")
    else:
        try:
            result = predictor.simular_computacao_quantica(n_qubits=n_qubits)
            if result:
                st.image(os.path.join(predictor.output_dir, "resultados_quanticos.png"), caption="Resultados Quânticos")
                st.image(os.path.join(predictor.output_dir, "numeros_quanticos.png"), caption="Números Previstos")
                st.success(f"Números previstos: {result['numeros_previstos']}")
        except Exception as e:
            st.error(f"Erro durante a simulação quântica: {e}")

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
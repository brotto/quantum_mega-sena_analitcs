from mega_sena_predictor import MegaSenaPredictor
from interprete_ia import interpretar_estabilidade_via_ia

def main():
    predictor = MegaSenaPredictor()

    print("🔄 Carregando dados...")
    if not predictor.carregar_dados():
        print("❌ Erro ao carregar dados.")
        return

    print("🔍 Detectando períodos de estabilidade...")
    predictor.detectar_periodos_estabilidade()

    # Tenta obter o período atual
    if predictor.periodos_estabilidade:
        periodo_atual = predictor.periodos_estabilidade[-1]
        print(f"\n📊 Último período identificado: Início no sorteio {periodo_atual['inicio']}, duração: {periodo_atual['tamanho']} sorteios.\n")
        
        print("🤖 Gerando interpretação da IA...")
        interpretacao = interpretar_estabilidade_via_ia(periodo_atual, len(predictor.periodos_estabilidade))

        if not interpretacao or interpretacao.strip() == "":
            print("⚠️ A IA não retornou nenhuma interpretação. Verifique se a chave OPENAI_API_KEY está corretamente configurada no arquivo .env.")

        print("\n💬 Interpretação do agente IA:")
        print("————————————————————————————————————————————")
        print(interpretacao)
        print("————————————————————————————————————————————")
    else:
        periodo_atual = None
        print("\n⚠️ Nenhum período atual de estabilidade foi identificado.\n")

if __name__ == "__main__":
    main()

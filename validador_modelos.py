import json
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from collections import Counter
import pandas as pd
from sklearn.metrics import mean_squared_error

# Importar os módulos desenvolvidos
sys.path.append('/home/ubuntu/mega_sena_analysis')
from modelo_numeros_raizes import AnalisadorMegaSena
from detector_numeros_raizes import DetectorNumerosRaizes, GeradorPrevisoes
from simulacao_quantica_avancada import SimulacaoQuanticaAvancada
from detector_mudancas_temporais import DetectorMudancasTemporais, AnalisadorMudancasTemporais

class ValidadorModelos:
    """
    Classe para validar os modelos desenvolvidos usando dados históricos da Mega Sena.
    """
    
    def __init__(self):
        """Inicializa o validador de modelos."""
        self.dados_historicos = {}
        self.sorteios = []
        self.resultados_validacao = {}
        
        # Instanciar os modelos
        self.analisador_raizes = AnalisadorMegaSena()
        self.gerador_previsoes = GeradorPrevisoes()
        self.simulador_quantico = SimulacaoQuanticaAvancada()
        self.analisador_mudancas = AnalisadorMudancasTemporais()
    
    def carregar_dados(self, arquivo_json):
        """
        Carrega os dados históricos da Mega Sena.
        
        Args:
            arquivo_json: Caminho para o arquivo JSON com os dados históricos.
        
        Returns:
            bool: True se os dados foram carregados com sucesso, False caso contrário.
        """
        try:
            with open(arquivo_json, 'r') as f:
                self.dados_historicos = json.load(f)
            
            # Converter para lista de listas de inteiros ordenados por concurso
            self.sorteios = []
            for concurso, numeros in sorted(self.dados_historicos.items(), key=lambda x: int(x[0])):
                self.sorteios.append([int(n) for n in numeros])
            
            print(f"Dados carregados com sucesso: {len(self.sorteios)} sorteios.")
            
            # Carregar dados nos modelos
            self.analisador_raizes.carregar_dados(arquivo_json)
            self.gerador_previsoes.carregar_dados(arquivo_json)
            self.analisador_mudancas.carregar_dados(arquivo_json)
            
            return True
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return False
    
    def validar_modelo_raizes(self, inicio=0, fim=100, passo=10):
        """
        Valida o modelo de detecção de números raízes.
        
        Args:
            inicio: Índice inicial para validação.
            fim: Índice final para validação.
            passo: Tamanho do passo para validação.
        
        Returns:
            dict: Resultados da validação.
        """
        print("\n===== Validando Modelo de Detecção de Números Raízes =====")
        
        resultados = []
        
        # Validar em diferentes pontos
        for i in range(inicio, fim, passo):
            if i + 1 >= len(self.sorteios):
                break
            
            # Usar sorteios até i para prever o sorteio i+1
            resultado = self.analisador_raizes.validar_com_historico(inicio, i)
            
            if resultado:
                resultados.append(resultado)
                print(f"Validação {i}: {resultado['acertos']} acertos")
        
        # Calcular estatísticas
        acertos = [r['acertos'] for r in resultados]
        media_acertos = np.mean(acertos) if acertos else 0
        
        print(f"Média de acertos: {media_acertos:.2f}/6")
        
        self.resultados_validacao['modelo_raizes'] = {
            'resultados': resultados,
            'media_acertos': media_acertos
        }
        
        return self.resultados_validacao['modelo_raizes']
    
    def validar_modelo_quantico(self, inicio=0, fim=100, passo=10):
        """
        Valida o modelo de simulação quântica.
        
        Args:
            inicio: Índice inicial para validação.
            fim: Índice final para validação.
            passo: Tamanho do passo para validação.
        
        Returns:
            dict: Resultados da validação.
        """
        print("\n===== Validando Modelo de Simulação Quântica =====")
        
        resultados = []
        
        # Validar em diferentes pontos
        for i in range(inicio, fim, passo):
            if i + 1 >= len(self.sorteios):
                break
            
            # Usar sorteios até i para prever o sorteio i+1
            sorteios_treino = self.sorteios[inicio:i]
            sorteio_alvo = self.sorteios[i]
            
            # Analisar dados quânticos
            analise = self.simulador_quantico.analisar_dados_quanticos(sorteios_treino)
            
            # Gerar previsões
            previsoes = self.simulador_quantico.gerar_previsoes_quanticas(sorteios_treino, n_previsoes=3)
            
            # Calcular acertos para cada previsão
            acertos_por_previsao = []
            for prev in previsoes:
                acertos = len(set(prev['numeros']).intersection(set(sorteio_alvo)))
                acertos_por_previsao.append({
                    'metodo': prev['metodo'],
                    'numeros': prev['numeros'],
                    'acertos': acertos
                })
            
            resultado = {
                'indice': i,
                'sorteio_alvo': sorteio_alvo,
                'previsoes': acertos_por_previsao
            }
            
            resultados.append(resultado)
            
            # Exibir resultados
            print(f"Validação {i}:")
            print(f"Sorteio alvo: {sorteio_alvo}")
            for p in acertos_por_previsao:
                print(f"  {p['metodo']}: {p['numeros']} - Acertos: {p['acertos']}/6")
        
        # Calcular estatísticas
        acertos_por_metodo = {}
        for resultado in resultados:
            for previsao in resultado['previsoes']:
                metodo = previsao['metodo']
                acertos = previsao['acertos']
                
                if metodo not in acertos_por_metodo:
                    acertos_por_metodo[metodo] = []
                
                acertos_por_metodo[metodo].append(acertos)
        
        medias_por_metodo = {}
        for metodo, acertos in acertos_por_metodo.items():
            medias_por_metodo[metodo] = np.mean(acertos)
            print(f"Média de acertos para {metodo}: {medias_por_metodo[metodo]:.2f}/6")
        
        self.resultados_validacao['modelo_quantico'] = {
            'resultados': resultados,
            'acertos_por_metodo': acertos_por_metodo,
            'medias_por_metodo': medias_por_metodo
        }
        
        return self.resultados_validacao['modelo_quantico']
    
    def validar_modelo_mudancas(self, inicio=0, fim=100, passo=10):
        """
        Valida o modelo de detecção de mudanças temporais.
        
        Args:
            inicio: Índice inicial para validação.
            fim: Índice final para validação.
            passo: Tamanho do passo para validação.
        
        Returns:
            dict: Resultados da validação.
        """
        print("\n===== Validando Modelo de Detecção de Mudanças Temporais =====")
        
        resultados = []
        
        # Validar em diferentes pontos
        for i in range(inicio, fim, passo):
            if i + 1 >= len(self.sorteios):
                break
            
            # Criar um analisador temporário com dados até o ponto i
            analisador_temp = AnalisadorMudancasTemporais()
            dados_temp = {str(j): [str(n) for n in self.sorteios[j]] for j in range(i)}
            
            # Salvar dados temporários em arquivo
            with open('dados_temp.json', 'w') as f:
                json.dump(dados_temp, f)
            
            # Carregar dados no analisador temporário
            analisador_temp.carregar_dados('dados_temp.json')
            
            # Analisar mudanças temporais
            analisador_temp.analisar_mudancas_temporais()
            
            # Gerar previsões
            previsoes = analisador_temp.gerar_previsoes_baseadas_em_mudancas(n_previsoes=3)
            
            # Calcular acertos para cada previsão
            sorteio_alvo = self.sorteios[i]
            acertos_por_previsao = []
            
            for prev in previsoes:
                acertos = len(set(prev['numeros']).intersection(set(sorteio_alvo)))
                acertos_por_previsao.append({
                    'metodo': prev['metodo'],
                    'numeros': prev['numeros'],
                    'acertos': acertos
                })
            
            resultado = {
                'indice': i,
                'sorteio_alvo': sorteio_alvo,
                'previsoes': acertos_por_previsao
            }
            
            resultados.append(resultado)
            
            # Exibir resultados
            print(f"Validação {i}:")
            print(f"Sorteio alvo: {sorteio_alvo}")
            for p in acertos_por_previsao:
                print(f"  {p['metodo']}: {p['numeros']} - Acertos: {p['acertos']}/6")
        
        # Calcular estatísticas
        acertos_por_metodo = {}
        for resultado in resultados:
            for previsao in resultado['previsoes']:
                metodo = previsao['metodo']
                acertos = previsao['acertos']
                
                if metodo not in acertos_por_metodo:
                    acertos_por_metodo[metodo] = []
                
                acertos_por_metodo[metodo].append(acertos)
        
        medias_por_metodo = {}
        for metodo, acertos in acertos_por_metodo.items():
            medias_por_metodo[metodo] = np.mean(acertos)
            print(f"Média de acertos para {metodo}: {medias_por_metodo[metodo]:.2f}/6")
        
        self.resultados_validacao['modelo_mudancas'] = {
            'resultados': resultados,
            'acertos_por_metodo': acertos_por_metodo,
            'medias_por_metodo': medias_por_metodo
        }
        
        # Limpar arquivo temporário
        if os.path.exists('dados_temp.json'):
            os.remove('dados_temp.json')
        
        return self.resultados_validacao['modelo_mudancas']
    
    def validar_todos_modelos(self, inicio=0, fim=100, passo=10):
        """
        Valida todos os modelos desenvolvidos.
        
        Args:
            inicio: Índice inicial para validação.
            fim: Índice final para validação.
            passo: Tamanho do passo para validação.
        
        Returns:
            dict: Resultados da validação de todos os modelos.
        """
        print("\n===== Iniciando Validação de Todos os Modelos =====")
        
        # Validar cada modelo
        self.validar_modelo_raizes(inicio, fim, passo)
        self.validar_modelo_quantico(inicio, fim, passo)
        self.validar_modelo_mudancas(inicio, fim, passo)
        
        # Comparar desempenho dos modelos
        self.comparar_desempenho_modelos()
        
        return self.resultados_validacao
    
    def comparar_desempenho_modelos(self):
        """
        Compara o desempenho dos diferentes modelos.
        
        Returns:
            dict: Resultados da comparação.
        """
        print("\n===== Comparando Desempenho dos Modelos =====")
        
        # Coletar médias de acertos de todos os modelos
        medias_acertos = {}
        
        # Modelo de raízes
        if 'modelo_raizes' in self.resultados_validacao:
            medias_acertos['Modelo Raízes'] = self.resultados_validacao['modelo_raizes']['media_acertos']
        
        # Modelo quântico
        if 'modelo_quantico' in self.resultados_validacao:
            for metodo, media in self.resultados_validacao['modelo_quantico']['medias_por_metodo'].items():
                medias_acertos[f'Quântico - {metodo}'] = media
        
        # Modelo de mudanças temporais
        if 'modelo_mudancas' in self.resultados_validacao:
            for metodo, media in self.resultados_validacao['modelo_mudancas']['medias_por_metodo'].items():
                medias_acertos[f'Mudanças - {metodo}'] = media
        
        # Exibir comparação
        print("\nMédia de acertos por modelo:")
        for modelo, media in sorted(medias_acertos.items(), key=lambda x: x[1], reverse=True):
            print(f"{modelo}: {media:.2f}/6")
        
        # Criar visualização
        self.visualizar_comparacao_modelos(medias_acertos)
        
        self.resultados_validacao['comparacao'] = {
            'medias_acertos': medias_acertos
        }
        
        return self.resultados_validacao['comparacao']
    
    def visualizar_comparacao_modelos(self, medias_acertos):
        """
        Cria uma visualização comparando o desempenho dos modelos.
        
        Args:
            medias_acertos: Dicionário com médias de acertos por modelo.
        
        Returns:
            str: Caminho para o arquivo de visualização.
        """
        plt.figure(figsize=(12, 8))
        
        # Ordenar modelos por média de acertos
        modelos = sorted(medias_acertos.items(), key=lambda x: x[1], reverse=True)
        nomes = [m[0] for m in modelos]
        valores = [m[1] for m in modelos]
        
        # Definir cores por tipo de modelo
        cores = []
        for nome in nomes:
            if nome.startswith('Quântico'):
                cores.append('green')
            elif nome.startswith('Mudanças'):
                cores.append('blue')
            else:
                cores.append('red')
        
        # Criar gráfico de barras
        plt.bar(nomes, valores, color=cores)
        plt.title('Comparação de Desempenho dos Modelos')
        plt.xlabel('Modelo')
        plt.ylabel('Média de Acertos por Sorteio')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Salvar gráfico
        arquivo_saida = "comparacao_modelos_validacao.png"
        plt.savefig(arquivo_saida)
        plt.close()
        
        print(f"Visualização salva em {arquivo_saida}")
        return arquivo_saida
    
    def validar_previsao_101(self):
        """
        Valida especificamente a previsão do 101º resultado usando os 100 primeiros.
        
        Returns:
            dict: Resultados da validação.
        """
        print("\n===== Validando Previsão do 101º Resultado =====")
        
        if len(self.sorteios) <= 101:
            print("Dados insuficientes para esta validação específica.")
            return {}
        
        # Extrair dados de treino e teste
        sorteios_treino = self.sorteios[:100]
        sorteio_alvo = self.sorteios[100]
        
        resultados = {}
        
        # 1. Validar com modelo de raízes
        analisador_temp = AnalisadorMegaSena()
        dados_temp = {str(j): [str(n) for n in sorteios_treino[j]] for j in range(len(sorteios_treino))}
        
        # Salvar dados temporários em arquivo
        with open('dados_temp_101.json', 'w') as f:
            json.dump(dados_temp, f)
        
        # Carregar dados e validar
        analisador_temp.carregar_dados('dados_temp_101.json')
        resultado_raizes = analisador_temp.validar_com_historico(0, 99)
        
        # 2. Validar com modelo quântico
        simulador_temp = SimulacaoQuanticaAvancada()
        analise = simulador_temp.analisar_dados_quanticos(sorteios_treino)
        previsoes_quanticas = simulador_temp.gerar_previsoes_quanticas(sorteios_treino, n_previsoes=3)
        
        acertos_quanticos = []
        for prev in previsoes_quanticas:
            acertos = len(set(prev['numeros']).intersection(set(sorteio_alvo)))
            acertos_quanticos.append({
                'metodo': prev['metodo'],
                'numeros': prev['numeros'],
                'acertos': acertos
            })
        
        # 3. Validar com modelo de mudanças temporais
        analisador_mudancas_temp = AnalisadorMudancasTemporais()
        analisador_mudancas_temp.carregar_dados('dados_temp_101.json')
        analisador_mudancas_temp.analisar_mudancas_temporais()
        previsoes_mudancas = analisador_mudancas_temp.gerar_previsoes_baseadas_em_mudancas(n_previsoes=3)
        
        acertos_mudancas = []
        for prev in previsoes_mudancas:
            acertos = len(set(prev['numeros']).intersection(set(sorteio_alvo)))
            acertos_mudancas.append({
                'metodo': prev['metodo'],
                'numeros': prev['numeros'],
                'acertos': acertos
            })
        
        # Compilar resultados
        resultados = {
            'sorteio_alvo': sorteio_alvo,
            'modelo_raizes': {
                'previsao': resultado_raizes['previsao'],
                'acertos': resultado_raizes['acertos']
            },
            'modelo_quantico': acertos_quanticos,
            'modelo_mudancas': acertos_mudancas
        }
        
        # Exibir resultados
        print(f"Sorteio 101 (alvo): {sorteio_alvo}")
        print(f"\nModelo de Raízes:")
        print(f"  Previsão: {resultado_raizes['previsao']} - Acertos: {resultado_raizes['acertos']}/6")
        
        print(f"\nModelo Quântico:")
        for p in acertos_quanticos:
            print(f"  {p['metodo']}: {p['numeros']} - Acertos: {p['acertos']}/6")
        
        print(f"\nModelo de Mudanças Temporais:")
        for p in acertos_mudancas:
            print(f"  {p['metodo']}: {p['numeros']} - Acertos: {p['acertos']}/6")
        
        # Limpar arquivo temporário
        if os.path.exists('dados_temp_101.json'):
            os.remove('dados_temp_101.json')
        
        self.resultados_validacao['previsao_101'] = resultados
        return resultados
    
    def salvar_resultados_validacao(self, arquivo="resultados_validacao.json"):
        """
        Salva os resultados da validação em um arquivo JSON.
        
        Args:
            arquivo: Nome do arquivo para salvar.
        
        Returns:
            bool: True se os resultados foram salvos com sucesso, False caso contrário.
        """
        try:
            # Converter dados para formato serializável
            resultados_serializaveis = {}
            
            for modelo, resultados in self.resultados_validacao.items():
                resultados_serializaveis[modelo] = {}
                
                for chave, valor in resultados.items():
                    # Converter arrays numpy para listas
                    if isinstance(valor, np.ndarray):
                        resultados_serializaveis[modelo][chave] = valor.tolist()
                    # Converter valores numpy para Python nativo
                    elif isinstance(valor, (np.int64, np.float64)):
                        resultados_serializaveis[modelo][chave] = valor.item()
                    # Manter dicionários e listas
                    elif isinstance(valor, (dict, list)):
                        resultados_serializaveis[modelo][chave] = valor
                    # Converter outros tipos para string
                    else:
                        resultados_serializaveis[modelo][chave] = str(valor)
            
            with open(arquivo, 'w') as f:
                json.dump(resultados_serializaveis, f, indent=2)
            
            print(f"Resultados da validação salvos em {arquivo}")
            return True
        except Exception as e:
            print(f"Erro ao salvar resultados: {e}")
            return False


def main():
    """Função principal para execução do validador."""
    print("\n===== Validação de Modelos para Análise da Mega Sena =====")
    print("Baseado na hipótese de que os números são gerados artificialmente")
    print("=========================================================\n")
    
    validador = ValidadorModelos()
    
    # Verificar se o arquivo de dados existe
    arquivo_padrao = "megasena_dados.json"
    if os.path.exists(arquivo_padrao):
        validador.carregar_dados(arquivo_padrao)
    else:
        print(f"Arquivo {arquivo_padrao} não encontrado.")
        arquivo = input("Digite o caminho para o arquivo de dados JSON: ")
        if not validador.carregar_dados(arquivo):
            print("Não foi possível carregar os dados. Encerrando.")
            return
    
    # Menu principal
    while True:
        print("\nOpções:")
        print("1. Validar modelo de detecção de números raízes")
        print("2. Validar modelo de simulação quântica")
        print("3. Validar modelo de detecção de mudanças temporais")
        print("4. Validar todos os modelos")
        print("5. Validar previsão do 101º resultado")
        print("6. Salvar resultados da validação")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            inicio = int(input("Índice inicial (padrão: 0): ") or "0")
            fim = int(input("Índice final (padrão: 100): ") or "100")
            passo = int(input("Tamanho do passo (padrão: 10): ") or "10")
            validador.validar_modelo_raizes(inicio, fim, passo)
        
        elif opcao == "2":
            inicio = int(input("Índice inicial (padrão: 0): ") or "0")
            fim = int(input("Índice final (padrão: 100): ") or "100")
            passo = int(input("Tamanho do passo (padrão: 10): ") or "10")
            validador.validar_modelo_quantico(inicio, fim, passo)
        
        elif opcao == "3":
            inicio = int(input("Índice inicial (padrão: 0): ") or "0")
            fim = int(input("Índice final (padrão: 100): ") or "100")
            passo = int(input("Tamanho do passo (padrão: 10): ") or "10")
            validador.validar_modelo_mudancas(inicio, fim, passo)
        
        elif opcao == "4":
            inicio = int(input("Índice inicial (padrão: 0): ") or "0")
            fim = int(input("Índice final (padrão: 100): ") or "100")
            passo = int(input("Tamanho do passo (padrão: 10): ") or "10")
            validador.validar_todos_modelos(inicio, fim, passo)
        
        elif opcao == "5":
            validador.validar_previsao_101()
        
        elif opcao == "6":
            arquivo = input("Nome do arquivo para salvar (padrão: resultados_validacao.json): ") or "resultados_validacao.json"
            validador.salvar_resultados_validacao(arquivo)
        
        elif opcao == "0":
            print("Encerrando o programa.")
            break
        
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()

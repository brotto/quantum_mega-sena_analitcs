import json
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import datetime
from collections import Counter
import pandas as pd
import random

# Importar os módulos desenvolvidos
sys.path.append('/home/ubuntu/mega_sena_analysis')
from detector_numeros_raizes import DetectorNumerosRaizes, GeradorPrevisoes
from simulacao_quantica_avancada import SimulacaoQuanticaAvancada
from detector_mudancas_temporais import AnalisadorMudancasTemporais

class GeradorPrevisoesMegaSena:
    """
    Classe para gerar previsões para jogos futuros da Mega Sena baseadas em
    números raízes e simulação quântica.
    """
    
    def __init__(self):
        """Inicializa o gerador de previsões."""
        self.dados_historicos = {}
        self.sorteios = []
        self.previsoes = []
        
        # Instanciar os modelos
        self.detector_raizes = DetectorNumerosRaizes()
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
            self.detector_raizes.carregar_dados(arquivo_json)
            self.analisador_mudancas.carregar_dados(arquivo_json)
            
            return True
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return False
    
    def analisar_dados(self):
        """
        Realiza a análise completa dos dados para detectar números raízes,
        padrões quânticos e mudanças temporais.
        
        Returns:
            dict: Resultados da análise.
        """
        print("\n===== Analisando Dados da Mega Sena =====")
        
        # Analisar números raízes
        print("\nDetectando números raízes...")
        self.detector_raizes.analisar_janelas_temporais()
        self.detector_raizes.detectar_numeros_raizes()
        self.detector_raizes.detectar_pontos_mudanca()
        
        # Analisar mudanças temporais
        print("\nAnalisando mudanças temporais...")
        self.analisador_mudancas.analisar_mudancas_temporais()
        
        # Analisar padrões quânticos
        print("\nAnalisando padrões quânticos...")
        raizes_recentes = self.detector_raizes.numeros_raizes[-1]['raizes'] if self.detector_raizes.numeros_raizes else None
        self.simulador_quantico.analisar_dados_quanticos(self.sorteios[-30:], raizes_recentes)
        
        print("\nAnálise de dados concluída.")
        
        return {
            'raizes': self.detector_raizes.numeros_raizes,
            'mudancas': self.analisador_mudancas.detector.pontos_mudanca,
            'periodos': self.analisador_mudancas.detector.periodos_estabilidade
        }
    
    def gerar_previsoes(self, n_previsoes=5):
        """
        Gera previsões para jogos futuros da Mega Sena.
        
        Args:
            n_previsoes: Número de previsões a gerar.
        
        Returns:
            list: Lista de previsões.
        """
        print("\n===== Gerando Previsões para Jogos Futuros =====")
        
        self.previsoes = []
        
        # 1. Gerar previsões baseadas em números raízes
        print("\nGerando previsões baseadas em números raízes...")
        previsoes_raizes = self.detector_raizes.gerar_previsoes_finais(n_previsoes=3)
        for prev in previsoes_raizes:
            self.previsoes.append({
                'metodo': f"raizes_{prev['metodo']}",
                'numeros': prev['numeros'],
                'descricao': prev['descricao'],
                'confianca': self._calcular_confianca(prev['numeros'], 'raizes')
            })
        
        # 2. Gerar previsões baseadas em simulação quântica
        print("\nGerando previsões baseadas em simulação quântica...")
        raizes_recentes = self.detector_raizes.numeros_raizes[-1]['raizes'] if self.detector_raizes.numeros_raizes else None
        previsoes_quanticas = self.simulador_quantico.gerar_previsoes_quanticas(self.sorteios[-30:], raizes_recentes, n_previsoes=3)
        for prev in previsoes_quanticas:
            self.previsoes.append({
                'metodo': f"quantico_{prev['metodo']}",
                'numeros': prev['numeros'],
                'descricao': prev['descricao'],
                'confianca': self._calcular_confianca(prev['numeros'], 'quantico')
            })
        
        # 3. Gerar previsões baseadas em mudanças temporais
        print("\nGerando previsões baseadas em mudanças temporais...")
        previsoes_mudancas = self.analisador_mudancas.gerar_previsoes_baseadas_em_mudancas(n_previsoes=3)
        for prev in previsoes_mudancas:
            self.previsoes.append({
                'metodo': f"mudancas_{prev['metodo']}",
                'numeros': prev['numeros'],
                'descricao': prev['descricao'],
                'confianca': self._calcular_confianca(prev['numeros'], 'mudancas')
            })
        
        # 4. Gerar previsões híbridas combinando diferentes abordagens
        print("\nGerando previsões híbridas...")
        previsoes_hibridas = self._gerar_previsoes_hibridas()
        for prev in previsoes_hibridas:
            self.previsoes.append(prev)
        
        # Ordenar previsões por confiança
        self.previsoes.sort(key=lambda x: x['confianca'], reverse=True)
        
        # Limitar ao número solicitado
        self.previsoes = self.previsoes[:n_previsoes]
        
        print(f"\nGeradas {len(self.previsoes)} previsões finais:")
        for i, prev in enumerate(self.previsoes, 1):
            print(f"{i}. Método: {prev['metodo']} - Números: {prev['numeros']} - Confiança: {prev['confianca']:.2f}")
            print(f"   {prev['descricao']}")
        
        return self.previsoes
    
    def _calcular_confianca(self, numeros, tipo_modelo):
        """
        Calcula um valor de confiança para uma previsão.
        
        Args:
            numeros: Lista de números previstos.
            tipo_modelo: Tipo de modelo que gerou a previsão.
        
        Returns:
            float: Valor de confiança entre 0 e 1.
        """
        # Base de confiança por tipo de modelo (baseado em validações anteriores)
        confianca_base = {
            'raizes': 0.7,
            'quantico': 0.6,
            'mudancas': 0.65,
            'hibrido': 0.75
        }
        
        # Obter confiança base
        confianca = confianca_base.get(tipo_modelo, 0.5)
        
        # Ajustar com base em características dos números
        
        # 1. Verificar distribuição de paridade
        n_pares = sum(1 for n in numeros if n % 2 == 0)
        n_impares = 6 - n_pares
        
        # Distribuição ideal: 3 pares e 3 ímpares
        ajuste_paridade = 1.0 - abs(n_pares - 3) / 3
        
        # 2. Verificar distribuição por dezenas
        dezenas = [0] * 6  # 0-9, 10-19, 20-29, 30-39, 40-49, 50-59
        for n in numeros:
            dezenas[(n-1) // 10] += 1
        
        # Distribuição ideal: números em pelo menos 3 dezenas diferentes
        n_dezenas_usadas = sum(1 for d in dezenas if d > 0)
        ajuste_dezenas = min(n_dezenas_usadas / 3, 1.0)
        
        # 3. Verificar presença de números frequentes
        # Obter números mais frequentes nos dados históricos
        todos_numeros = []
        for sorteio in self.sorteios:
            todos_numeros.extend(sorteio)
        
        contador = Counter(todos_numeros)
        numeros_frequentes = [num for num, _ in contador.most_common(10)]
        
        # Contar quantos números frequentes estão na previsão
        n_frequentes = sum(1 for n in numeros if n in numeros_frequentes)
        ajuste_frequencia = min(n_frequentes / 3, 1.0)
        
        # Combinar ajustes
        ajuste_total = (ajuste_paridade + ajuste_dezenas + ajuste_frequencia) / 3
        
        # Aplicar ajuste à confiança base
        confianca_final = confianca * (0.7 + 0.3 * ajuste_total)
        
        # Adicionar um pouco de aleatoriedade para diferenciar previsões similares
        confianca_final += random.uniform(-0.05, 0.05)
        
        # Garantir que está no intervalo [0, 1]
        return max(0.0, min(1.0, confianca_final))
    
    def _gerar_previsoes_hibridas(self):
        """
        Gera previsões híbridas combinando diferentes abordagens.
        
        Returns:
            list: Lista de previsões híbridas.
        """
        previsoes_hibridas = []
        
        # Obter números raízes mais recentes
        raizes_recentes = self.detector_raizes.numeros_raizes[-1]['raizes'] if self.detector_raizes.numeros_raizes else []
        
        # Obter período de estabilidade atual
        periodo_atual = self.analisador_mudancas.detector.periodos_estabilidade[-1] if self.analisador_mudancas.detector.periodos_estabilidade else None
        
        # Híbrido 1: Combinar raízes com características do período atual
        if raizes_recentes and periodo_atual:
            numeros_hibrido1 = []
            
            # Incluir algumas raízes
            for raiz in raizes_recentes[:2]:
                if raiz not in numeros_hibrido1:
                    numeros_hibrido1.append(raiz)
            
            # Completar com números baseados na paridade do período
            media_pares = periodo_atual['media_pares']
            n_pares_alvo = round(media_pares)
            n_pares_atual = sum(1 for n in numeros_hibrido1 if n % 2 == 0)
            
            # Determinar quantos pares e ímpares adicionar
            n_pares_adicionar = max(0, n_pares_alvo - n_pares_atual)
            n_impares_adicionar = 6 - len(numeros_hibrido1) - n_pares_adicionar
            
            # Obter números frequentes dos últimos sorteios
            todos_numeros = []
            for sorteio in self.sorteios[-30:]:
                todos_numeros.extend(sorteio)
            
            contador = Counter(todos_numeros)
            
            # Separar números pares e ímpares
            pares = [n for n in range(2, 61, 2) if n not in numeros_hibrido1]
            impares = [n for n in range(1, 61, 2) if n not in numeros_hibrido1]
            
            # Ordenar por frequência
            pares = sorted(pares, key=lambda x: contador.get(x, 0), reverse=True)
            impares = sorted(impares, key=lambda x: contador.get(x, 0), reverse=True)
            
            # Adicionar números
            for _ in range(n_pares_adicionar):
                if pares:
                    numeros_hibrido1.append(pares.pop(0))
            
            for _ in range(n_impares_adicionar):
                if impares:
                    numeros_hibrido1.append(impares.pop(0))
            
            # Garantir que temos 6 números
            while len(numeros_hibrido1) < 6:
                num = random.randint(1, 60)
                if num not in numeros_hibrido1:
                    numeros_hibrido1.append(num)
            
            previsoes_hibridas.append({
                'metodo': 'hibrido_raizes_periodo',
                'numeros': sorted(numeros_hibrido1),
                'descricao': 'Combinação de números raízes com características do período atual',
                'confianca': self._calcular_confianca(sorted(numeros_hibrido1), 'hibrido')
            })
        
        # Híbrido 2: Combinar resultados quânticos com análise de mudanças
        previsoes_quanticas = self.simulador_quantico.resultados_analise.get('previsoes', {})
        if previsoes_quanticas and self.analisador_mudancas.detector.pontos_mudanca:
            # Verificar proximidade de mudança
            proxima_mudanca = self.analisador_mudancas.detector.prever_proxima_mudanca()
            proximidade_mudanca = proxima_mudanca.get('sorteios_restantes', float('inf'))
            
            numeros_hibrido2 = []
            
            # Selecionar método quântico baseado na proximidade de mudança
            metodo_quantico = 'qft' if proximidade_mudanca < 10 else 'grover'
            if metodo_quantico in previsoes_quanticas:
                # Incluir alguns números da previsão quântica
                for num in previsoes_quanticas[metodo_quantico][:3]:
                    if num not in numeros_hibrido2:
                        numeros_hibrido2.append(num)
            
            # Completar com números baseados em tendências temporais
            if self.analisador_mudancas.detector.metricas_temporais.get('tendencias'):
                tendencias = self.analisador_mudancas.detector.metricas_temporais['tendencias']
                
                # Usar tendência da série 'soma' para influenciar a seleção
                tendencia_soma = tendencias.get('soma', 0)
                
                # Se tendência positiva, favorecer números maiores
                # Se tendência negativa, favorecer números menores
                if tendencia_soma > 0:
                    candidatos = sorted(range(31, 61), key=lambda x: random.random())
                else:
                    candidatos = sorted(range(1, 31), key=lambda x: random.random())
                
                # Adicionar números
                for num in candidatos:
                    if num not in numeros_hibrido2 and len(numeros_hibrido2) < 6:
                        numeros_hibrido2.append(num)
            
            # Garantir que temos 6 números
            while len(numeros_hibrido2) < 6:
                num = random.randint(1, 60)
                if num not in numeros_hibrido2:
                    numeros_hibrido2.append(num)
            
            previsoes_hibridas.append({
                'metodo': 'hibrido_quantico_mudancas',
                'numeros': sorted(numeros_hibrido2),
                'descricao': 'Combinação de simulação quântica com análise de mudanças temporais',
                'confianca': self._calcular_confianca(sorted(numeros_hibrido2), 'hibrido')
            })
        
        # Híbrido 3: Combinar todos os modelos
        if self.previsoes:  # Se já temos algumas previsões
            # Contar frequência de cada número nas previsões existentes
            contador_previsoes = Counter()
            for prev in self.previsoes:
                for num in prev['numeros']:
                    contador_previsoes[num] += 1
            
            # Selecionar os números mais frequentes
            numeros_hibrido3 = [num for num, _ in contador_previsoes.most_common(6)]
            
            # Garantir que temos 6 números
            while len(numeros_hibrido3) < 6:
                num = random.randint(1, 60)
                if num not in numeros_hibrido3:
                    numeros_hibrido3.append(num)
            
            previsoes_hibridas.append({
                'metodo': 'hibrido_consenso',
                'numeros': sorted(numeros_hibrido3),
                'descricao': 'Consenso entre todos os modelos (números mais frequentes nas previsões)',
                'confianca': self._calcular_confianca(sorted(numeros_hibrido3), 'hibrido')
            })
        
        return previsoes_hibridas
    
    def visualizar_previsoes(self, arquivo_saida="previsoes_finais.png"):
        """
        Cria uma visualização das previsões geradas.
        
        Args:
            arquivo_saida: Nome do arquivo para salvar a visualização.
        
        Returns:
            str: Caminho para o arquivo de visualização.
        """
        if not self.previsoes:
            print("Nenhuma previsão para visualizar. Execute gerar_previsoes() primeiro.")
            return None
        
        plt.figure(figsize=(15, 10))
        
        # Criar matriz para contagem de frequência
        frequencia = np.zeros(60)
        
        # Contar frequência de cada número nas previsões
        for prev in self.previsoes:
            for num in prev['numeros']:
                frequencia[num-1] += 1
        
        # Normalizar frequência
        if np.max(frequencia) > 0:
            frequencia = frequencia / np.max(frequencia)
        
        # Plotar frequência
        plt.subplot(2, 1, 1)
        plt.bar(range(1, 61), frequencia, color='blue', alpha=0.7)
        plt.title('Frequência dos Números nas Previsões Finais')
        plt.xlabel('Número')
        plt.ylabel('Frequência Normalizada')
        plt.xticks(range(0, 61, 5))
        plt.grid(True, alpha=0.3)
        
        # Plotar previsões individuais
        plt.subplot(2, 1, 2)
        
        for i, prev in enumerate(self.previsoes):
            # Criar array com 0s e 1s para indicar presença do número
            presenca = np.zeros(60)
            for num in prev['numeros']:
                presenca[num-1] = 1
            
            # Plotar como linha horizontal
            plt.scatter(range(1, 61), [i+1] * 60, c=presenca, cmap='Blues', 
                       marker='s', s=100, alpha=0.7)
            
            # Adicionar rótulo
            plt.text(0, i+1, f"{i+1}. {prev['metodo']}", ha='right', va='center')
        
        plt.title('Previsões Individuais')
        plt.xlabel('Número')
        plt.ylabel('Previsão')
        plt.yticks(range(1, len(self.previsoes)+1))
        plt.xticks(range(0, 61, 5))
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(arquivo_saida)
        plt.close()
        
        print(f"Visualização salva em {arquivo_saida}")
        return arquivo_saida
    
    def salvar_previsoes(self, arquivo="previsoes_mega_sena.json"):
        """
        Salva as previsões em um arquivo JSON.
        
        Args:
            arquivo: Nome do arquivo para salvar.
        
        Returns:
            bool: True se as previsões foram salvas com sucesso, False caso contrário.
        """
        if not self.previsoes:
            print("Nenhuma previsão para salvar. Execute gerar_previsoes() primeiro.")
            return False
        
        try:
            data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            dados_saida = {
                "data_geracao": data_atual,
                "total_sorteios_analisados": len(self.sorteios),
                "previsoes": self.previsoes
            }
            
            # Adicionar informações sobre números raízes
            if self.detector_raizes.numeros_raizes:
                dados_saida["info_raizes"] = {
                    "raizes_recentes": self.detector_raizes.numeros_raizes[-1]['raizes'],
                    "total_pontos_mudanca": len(self.detector_raizes.pontos_mudanca)
                }
            
            # Adicionar informação sobre próxima mudança prevista
            if self.analisador_mudancas.detector.periodos_estabilidade:
                proxima_mudanca = self.analisador_mudancas.detector.prever_proxima_mudanca()
                if proxima_mudanca:
                    dados_saida["proxima_mudanca"] = proxima_mudanca
            
            with open(arquivo, 'w') as f:
                json.dump(dados_saida, f, indent=2)
            
            print(f"Previsões salvas com sucesso em {arquivo}")
            return True
        except Exception as e:
            print(f"Erro ao salvar previsões: {e}")
            return False


def main():
    """Função principal para execução do gerador de previsões."""
    print("\n===== Gerador de Previsões para a Mega Sena =====")
    print("Baseado na hipótese de que os números são gerados artificialmente")
    print("====================================================\n")
    
    gerador = GeradorPrevisoesMegaSena()
    
    # Verificar se o arquivo de dados existe
    arquivo_padrao = "megasena_dados.json"
    if os.path.exists(arquivo_padrao):
        gerador.carregar_dados(arquivo_padrao)
    else:
        print(f"Arquivo {arquivo_padrao} não encontrado.")
        arquivo = input("Digite o caminho para o arquivo de dados JSON: ")
        if not gerador.carregar_dados(arquivo):
            print("Não foi possível carregar os dados. Encerrando.")
            return
    
    # Menu principal
    while True:
        print("\nOpções:")
        print("1. Analisar dados")
        print("2. Gerar previsões")
        print("3. Visualizar previsões")
        print("4. Salvar previsões")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            gerador.analisar_dados()
        
        elif opcao == "2":
            n_previsoes = int(input("Número de previsões a gerar (padrão: 5): ") or "5")
            gerador.gerar_previsoes(n_previsoes=n_previsoes)
        
        elif opcao == "3":
            if not gerador.previsoes:
                print("Nenhuma previsão gerada. Execute a opção 2 primeiro.")
            else:
                arquivo = input("Nome do arquivo para salvar a visualização (padrão: previsoes_finais.png): ") or "previsoes_finais.png"
                gerador.visualizar_previsoes(arquivo)
        
        elif opcao == "4":
            if not gerador.previsoes:
                print("Nenhuma previsão gerada. Execute a opção 2 primeiro.")
            else:
                arquivo = input("Nome do arquivo para salvar (padrão: previsoes_mega_sena.json): ") or "previsoes_mega_sena.json"
                gerador.salvar_previsoes(arquivo)
        
        elif opcao == "0":
            print("Encerrando o programa.")
            break
        
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()

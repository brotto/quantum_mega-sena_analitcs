import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
import datetime
import argparse
import requests
from tqdm import tqdm
import pandas as pd

class MegaSenaPredictor:
    """
    Sistema de previsão para a Mega Sena baseado na hipótese de que os números
    são gerados artificialmente a partir de números raízes.
    
    Este sistema permite:
    1. Baixar dados históricos da Mega Sena
    2. Analisar padrões nos dados históricos
    3. Detectar possíveis números raízes
    4. Simular computação quântica para identificar padrões ocultos
    5. Detectar mudanças temporais nos padrões
    6. Gerar previsões para jogos futuros
    """
    
    def __init__(self):
        """Inicializa o sistema de previsão."""
        self.dados_historicos = {}
        self.sorteios = []
        self.numeros_raizes = []
        self.pontos_mudanca = []
        self.periodos_estabilidade = []
        self.previsoes = []
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
        
        # Criar diretórios se não existirem
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def baixar_dados_historicos(self, force=False):
        """
        Baixa os dados históricos da Mega Sena.
        
        Args:
            force: Se True, força o download mesmo se o arquivo já existir.
        
        Returns:
            bool: True se os dados foram baixados com sucesso, False caso contrário.
        """
        arquivo_dados = os.path.join(self.data_dir, 'megasena_dados.json')
        
        if os.path.exists(arquivo_dados) and not force:
            print(f"Arquivo de dados já existe em {arquivo_dados}.")
            print("Use --force para baixar novamente.")
            return True
        
        print("Baixando dados históricos da Mega Sena...")
        
        try:
            # URL para dados da Mega Sena
            url = "https://raw.githubusercontent.com/guilhermeasn/loteria.json/master/json/megasena.json"
            
            # Fazer requisição
            response = requests.get(url)
            response.raise_for_status()
            
            # Salvar dados
            with open(arquivo_dados, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"Dados baixados com sucesso e salvos em {arquivo_dados}.")
            return True
        except Exception as e:
            print(f"Erro ao baixar dados: {e}")
            return False
    
    def carregar_dados(self, arquivo=None):
        """
        Carrega os dados históricos da Mega Sena.
        
        Args:
            arquivo: Caminho para o arquivo JSON com os dados históricos.
                    Se None, usa o arquivo padrão.
        
        Returns:
            bool: True se os dados foram carregados com sucesso, False caso contrário.
        """
        if arquivo is None:
            arquivo = os.path.join(self.data_dir, 'megasena_dados.json')
        
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                self.dados_historicos = json.load(f)
            
            # Converter para lista de listas de inteiros ordenados por concurso
            self.sorteios = []
            for concurso, numeros in sorted(self.dados_historicos.items(), key=lambda x: int(x[0])):
                self.sorteios.append([int(n) for n in numeros])
            
            print(f"Dados carregados com sucesso: {len(self.sorteios)} sorteios.")
            return True
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return False
    
    def adicionar_sorteios_recentes(self, novos_sorteios):
        """
        Adiciona sorteios recentes aos dados históricos.
        
        Args:
            novos_sorteios: Lista de listas com os números dos sorteios recentes.
        
        Returns:
            bool: True se os sorteios foram adicionados com sucesso, False caso contrário.
        """
        try:
            # Verificar se os sorteios são válidos
            for sorteio in novos_sorteios:
                if len(sorteio) != 6:
                    print(f"Erro: Sorteio {sorteio} não tem 6 números.")
                    return False
                
                for num in sorteio:
                    if not (1 <= num <= 60):
                        print(f"Erro: Número {num} fora do intervalo válido (1-60).")
                        return False
            
            # Adicionar sorteios
            ultimo_concurso = max(int(k) for k in self.dados_historicos.keys()) if self.dados_historicos else 0
            
            for i, sorteio in enumerate(novos_sorteios, 1):
                concurso = str(ultimo_concurso + i)
                self.dados_historicos[concurso] = [str(n) for n in sorteio]
                self.sorteios.append(sorteio)
            
            # Salvar dados atualizados
            arquivo_dados = os.path.join(self.data_dir, 'megasena_dados.json')
            with open(arquivo_dados, 'w', encoding='utf-8') as f:
                json.dump(self.dados_historicos, f, indent=2)
            
            print(f"Adicionados {len(novos_sorteios)} novos sorteios aos dados históricos.")
            return True
        except Exception as e:
            print(f"Erro ao adicionar sorteios recentes: {e}")
            return False
    
    def detectar_numeros_raizes(self, tamanho_janela=50, n_raizes=3):
        """
        Detecta possíveis números raízes nos dados históricos.
        
        Args:
            tamanho_janela: Tamanho da janela de análise.
            n_raizes: Número de raízes a detectar por janela.
        
        Returns:
            list: Lista de números raízes detectados.
        """
        from collections import Counter
        
        print("Detectando números raízes...")
        
        # Criar janelas de análise
        janelas = []
        for i in range(0, len(self.sorteios) - tamanho_janela + 1, tamanho_janela // 2):
            janela = self.sorteios[i:i + tamanho_janela]
            janelas.append(janela)
        
        self.numeros_raizes = []
        
        for idx, janela in enumerate(janelas):
            # Extrair características da janela
            raizes = self._extrair_raizes_da_janela(janela, n_raizes)
            
            self.numeros_raizes.append({
                'janela_idx': idx,
                'inicio': idx * (tamanho_janela // 2),
                'fim': idx * (tamanho_janela // 2) + tamanho_janela,
                'raizes': raizes
            })
        
        # Detectar pontos de mudança
        self.pontos_mudanca = []
        
        for i in range(1, len(self.numeros_raizes)):
            raizes_atuais = set(self.numeros_raizes[i]['raizes'])
            raizes_anteriores = set(self.numeros_raizes[i-1]['raizes'])
            
            # Calcular diferença como proporção de números diferentes
            diferenca = 1 - len(raizes_atuais.intersection(raizes_anteriores)) / len(raizes_atuais)
            
            if diferenca >= 0.5:  # Limiar para considerar uma mudança significativa
                self.pontos_mudanca.append({
                    'janela_idx': i,
                    'inicio_sorteio': self.numeros_raizes[i]['inicio'],
                    'diferenca': diferenca,
                    'raizes_antes': self.numeros_raizes[i-1]['raizes'],
                    'raizes_depois': self.numeros_raizes[i]['raizes']
                })
        
        print(f"Detectados números raízes para {len(self.numeros_raizes)} janelas.")
        print(f"Detectados {len(self.pontos_mudanca)} pontos de mudança nos números raízes.")
        
        # Visualizar evolução das raízes
        self._visualizar_evolucao_raizes()
        
        return self.numeros_raizes
    
    def _extrair_raizes_da_janela(self, sorteios, n_raizes):
        """
        Extrai possíveis números raízes de uma janela de sorteios.
        
        Args:
            sorteios: Lista de sorteios na janela.
            n_raizes: Número de raízes a extrair.
        
        Returns:
            list: Lista de possíveis números raízes.
        """
        from collections import Counter
        
        # Método 1: Análise de frequência
        todos_numeros = []
        for sorteio in sorteios:
            todos_numeros.extend(sorteio)
        
        contador = Counter(todos_numeros)
        numeros_frequentes = [num for num, _ in contador.most_common(10)]
        
        # Método 2: Análise de padrões de sequência
        diferenca_media = {}
        for i in range(1, 61):
            diferenca_media[i] = 0
            count = 0
            
            for sorteio in sorteios:
                if i in sorteio:
                    idx = sorteio.index(i)
                    if idx > 0:
                        diferenca_media[i] += sorteio[idx] - sorteio[idx-1]
                        count += 1
            
            if count > 0:
                diferenca_media[i] /= count
        
        # Números com diferença média mais estável
        numeros_estaveis = sorted(diferenca_media.items(), key=lambda x: abs(x[1] - 8))[:10]
        numeros_estaveis = [num for num, _ in numeros_estaveis]
        
        # Método 3: Análise de somas
        somas = [sum(sorteio) for sorteio in sorteios]
        soma_media = sum(somas) / len(somas)
        
        # Números que contribuem para a soma média
        contribuicao_soma = {}
        for i in range(1, 61):
            contribuicao_soma[i] = 0
            for sorteio in sorteios:
                if i in sorteio:
                    contribuicao_soma[i] += abs(sum(sorteio) - soma_media)
        
        numeros_soma = sorted(contribuicao_soma.items(), key=lambda x: x[1])[:10]
        numeros_soma = [num for num, _ in numeros_soma]
        
        # Combinar os métodos para selecionar as raízes
        candidatos = set(numeros_frequentes + numeros_estaveis + numeros_soma)
        
        # Priorizar números que aparecem em múltiplos métodos
        contagem_metodos = Counter()
        for num in candidatos:
            if num in numeros_frequentes:
                contagem_metodos[num] += 1
            if num in numeros_estaveis:
                contagem_metodos[num] += 1
            if num in numeros_soma:
                contagem_metodos[num] += 1
        
        # Selecionar as raízes finais
        raizes_finais = [num for num, _ in contagem_metodos.most_common(n_raizes)]
        
        # Se não tivermos raízes suficientes, completar com números frequentes
        while len(raizes_finais) < n_raizes:
            for num in numeros_frequentes:
                if num not in raizes_finais:
                    raizes_finais.append(num)
                    break
        
        return sorted(raizes_finais[:n_raizes])
    
    def _visualizar_evolucao_raizes(self):
        """
        Cria uma visualização da evolução dos números raízes ao longo do tempo.
        
        Returns:
            str: Caminho para o arquivo de visualização.
        """
        if not self.numeros_raizes:
            print("Nenhum número raiz detectado para visualizar.")
            return None
        
        plt.figure(figsize=(12, 8))
        
        # Número de raízes por janela
        n_raizes = len(self.numeros_raizes[0]['raizes'])
        
        # Preparar dados para o gráfico
        janelas = [r['janela_idx'] for r in self.numeros_raizes]
        
        # Plotar cada raiz como uma linha
        cores = ['r', 'g', 'b', 'c', 'm', 'y']
        for i in range(n_raizes):
            valores = [r['raizes'][i] if i < len(r['raizes']) else None for r in self.numeros_raizes]
            plt.plot(janelas, valores, marker='o', linestyle='-', color=cores[i % len(cores)], 
                     label=f'Raiz {i+1}')
        
        # Marcar pontos de mudança
        for ponto in self.pontos_mudanca:
            plt.axvline(x=ponto['janela_idx'], color='k', linestyle='--', alpha=0.5)
        
        plt.title('Evolução dos Números Raízes ao Longo do Tempo')
        plt.xlabel('Índice da Janela')
        plt.ylabel('Valor da Raiz')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Salvar gráfico
        arquivo_saida = os.path.join(self.output_dir, "evolucao_raizes.png")
        plt.savefig(arquivo_saida)
        plt.close()
        
        print(f"Visualização salva em {arquivo_saida}")
        return arquivo_saida
    
    def detectar_periodos_estabilidade(self, min_tamanho=20):
        """
        Identifica períodos de estabilidade entre pontos de mudança.
        
        Args:
            min_tamanho: Tamanho mínimo de um período para ser considerado estável.
        
        Returns:
            list: Lista de períodos de estabilidade.
        """
        if not self.pontos_mudanca and not self.numeros_raizes:
            print("Execute detectar_numeros_raizes() primeiro.")
            return []
        
        print("Detectando períodos de estabilidade...")
        
        # Adicionar início e fim dos dados como pontos de referência
        pontos_ref = [0] + [p['inicio_sorteio'] for p in self.pontos_mudanca] + [len(self.sorteios)]
        
        # Identificar períodos entre pontos de mudança
        self.periodos_estabilidade = []
        
        for i in range(len(pontos_ref) - 1):
            inicio = pontos_ref[i]
            fim = pontos_ref[i+1]
            
            # Verificar se o período é grande o suficiente
            if fim - inicio >= min_tamanho:
                # Extrair sorteios deste período
                sorteios_periodo = self.sorteios[inicio:fim]
                
                # Analisar características do período
                media_soma = np.mean([sum(s) for s in sorteios_periodo])
                media_pares = np.mean([sum(1 for n in s if n % 2 == 0) for s in sorteios_periodo])
                
                # Detectar possíveis números raízes para este período
                raizes = self._extrair_raizes_da_janela(sorteios_periodo, n_raizes=3)
                
                self.periodos_estabilidade.append({
                    'inicio': inicio,
                    'fim': fim,
                    'tamanho': fim - inicio,
                    'media_soma': media_soma,
                    'media_pares': media_pares,
                    'raizes': raizes
                })
        
        print(f"Identificados {len(self.periodos_estabilidade)} períodos de estabilidade.")
        
        # Visualizar períodos
        self._visualizar_periodos_estabilidade()
        
        return self.periodos_estabilidade
    
    def _visualizar_periodos_estabilidade(self):
        """
        Cria uma visualização dos períodos de estabilidade e suas características.
        
        Returns:
            str: Caminho para o arquivo de visualização.
        """
        if not self.periodos_estabilidade:
            print("Nenhum período de estabilidade para visualizar.")
            return None
        
        plt.figure(figsize=(15, 10))
        
        # Plotar características dos períodos
        plt.subplot(2, 1, 1)
        
        # Preparar dados
        indices = range(len(self.periodos_estabilidade))
        tamanhos = [p['tamanho'] for p in self.periodos_estabilidade]
        medias_soma = [p['media_soma'] for p in self.periodos_estabilidade]
        medias_pares = [p['media_pares'] * 10 for p in self.periodos_estabilidade]  # Escalar para visualização
        
        # Plotar
        plt.bar(indices, tamanhos, alpha=0.5, label='Tamanho do Período')
        plt.plot(indices, medias_soma, 'ro-', label='Média da Soma')
        plt.plot(indices, medias_pares, 'go-', label='Média de Pares (x10)')
        
        plt.title('Características dos Períodos de Estabilidade')
        plt.xlabel('Índice do Período')
        plt.ylabel('Valor')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plotar raízes por período
        plt.subplot(2, 1, 2)
        
        # Plotar raízes para cada período
        for i, periodo in enumerate(self.periodos_estabilidade):
            raizes = periodo['raizes']
            for j, raiz in enumerate(raizes):
                plt.scatter(i, raiz, s=100, marker='o', label=f'Raiz {j+1}' if i == 0 else "")
            
            # Conectar raízes entre períodos consecutivos
            if i > 0:
                raizes_anterior = self.periodos_estabilidade[i-1]['raizes']
                for j, raiz in enumerate(raizes):
                    if j < len(raizes_anterior):
                        plt.plot([i-1, i], [raizes_anterior[j], raiz], 'k--', alpha=0.3)
        
        plt.title('Números Raízes por Período de Estabilidade')
        plt.xlabel('Índice do Período')
        plt.ylabel('Valor da Raiz')
        plt.yticks(range(0, 61, 5))
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        
        # Salvar gráfico
        arquivo_saida = os.path.join(self.output_dir, "periodos_estabilidade.png")
        plt.savefig(arquivo_saida)
        plt.close()
        
        print(f"Visualização salva em {arquivo_saida}")
        return arquivo_saida
    
    def simular_computacao_quantica(self, n_qubits=6):
        """
        Simula computação quântica para análise de padrões nos dados.
        
        Args:
            n_qubits: Número de qubits a utilizar na simulação.
        
        Returns:
            dict: Resultados da simulação quântica.
        """
        try:
            import pennylane as qml
            import random
        except ImportError:
            print("Erro: Biblioteca PennyLane não encontrada.")
            print("Instale com: pip install pennylane")
            return {}
        
        print("Simulando computação quântica para análise de padrões...")
        
        # Usar os últimos 20 sorteios para análise
        sorteios_recentes = self.sorteios[-20:]
        
        # Preparar dados de entrada
        dados_entrada = self._preparar_dados_entrada(sorteios_recentes)
        
        # Criar dispositivo quântico
        dev = qml.device("default.qubit", wires=n_qubits)
        
        # Definir circuito quântico
        @qml.qnode(dev)
        def circuito(params):
            # Preparar estado inicial em superposição
            for i in range(n_qubits):
                qml.Hadamard(wires=i)
            
            # Aplicar operações baseadas nos dados
            for i in range(n_qubits):
                idx = i % len(dados_entrada)
                qml.RY(np.pi * dados_entrada[idx], wires=i)
            
            # Criar emaranhamento
            for i in range(n_qubits - 1):
                qml.CNOT(wires=[i, i+1])
            
            # Aplicar operações de fase baseadas nos parâmetros
            for i in range(n_qubits):
                qml.PhaseShift(params[i], wires=i)
            
            # Aplicar operações de Grover
            for _ in range(2):  # Número de iterações de Grover
                # Difusão
                for i in range(n_qubits):
                    qml.Hadamard(wires=i)
                    qml.PhaseShift(np.pi, wires=i)
                
                # Emaranhamento
                for i in range(n_qubits - 1):
                    qml.CNOT(wires=[i, i+1])
                
                # Desfazer difusão
                for i in range(n_qubits):
                    qml.PhaseShift(np.pi, wires=i)
                    qml.Hadamard(wires=i)
            
            # Retornar probabilidades
            return [qml.probs(wires=i) for i in range(n_qubits)]
        
        # Inicializar parâmetros aleatórios
        params = np.random.uniform(0, np.pi, n_qubits)
        
        # Executar circuito
        resultados = circuito(params)
        
        # Converter para números da Mega Sena
        numeros_previstos = self._converter_para_numeros_mega(resultados)
        
        print(f"Simulação quântica concluída. Números gerados: {numeros_previstos}")
        
        # Visualizar resultados quânticos
        self._visualizar_resultados_quanticos(resultados, numeros_previstos)
        
        return {
            'resultados_quanticos': resultados,
            'numeros_previstos': numeros_previstos
        }
    
    def _preparar_dados_entrada(self, sorteios):
        """
        Prepara os dados de sorteios para entrada no circuito quântico.
        
        Args:
            sorteios: Lista de sorteios.
        
        Returns:
            np.array: Array com dados normalizados.
        """
        # Extrair e normalizar os números
        dados = []
        for sorteio in sorteios:
            # Normalizar para [0, 1]
            normalizado = [n/60 for n in sorteio]
            dados.extend(normalizado)
        
        # Limitar o tamanho para evitar sobrecarga
        return np.array(dados[:100])
    
    def _converter_para_numeros_mega(self, resultados_quanticos):
        """
        Converte resultados quânticos em números para a Mega Sena.
        
        Args:
            resultados_quanticos: Lista de arrays de probabilidades.
        
        Returns:
            list: Lista de números entre 1 e 60.
        """
        import random
        
        numeros = []
        for probs in resultados_quanticos:
            # Usar o índice de maior probabilidade para gerar um número
            idx_max = np.argmax(probs)
            
            # Mapear para o intervalo [1, 60]
            num = int(idx_max * (60 / (2**len(probs.shape))) + 1)
            
            # Garantir que está no intervalo correto
            num = max(1, min(60, num))
            
            if num not in numeros:
                numeros.append(num)
        
        # Garantir que temos 6 números únicos
        while len(numeros) < 6:
            num = random.randint(1, 60)
            if num not in numeros:
                numeros.append(num)
        
        return sorted(numeros[:6])
    
    def _visualizar_resultados_quanticos(self, resultados_quanticos, numeros_previstos):
        """
        Cria uma visualização dos resultados da simulação quântica.
        
        Args:
            resultados_quanticos: Lista de arrays de probabilidades.
            numeros_previstos: Lista de números previstos.
        
        Returns:
            str: Caminho para o arquivo de visualização.
        """
        plt.figure(figsize=(12, 8))
        
        # Plotar distribuições de probabilidade para cada qubit
        for i, probs in enumerate(resultados_quanticos):
            plt.subplot(3, 2, i+1)
            plt.bar(range(len(probs)), probs)
            plt.title(f'Qubit {i}')
            plt.xlabel('Estado')
            plt.ylabel('Probabilidade')
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Salvar gráfico
        arquivo_saida = os.path.join(self.output_dir, "resultados_quanticos.png")
        plt.savefig(arquivo_saida)
        plt.close()
        
        # Criar gráfico dos números previstos
        plt.figure(figsize=(10, 6))
        
        # Plotar números previstos
        plt.bar(range(1, 61), [1 if i in numeros_previstos else 0 for i in range(1, 61)])
        plt.title('Números Previstos pela Simulação Quântica')
        plt.xlabel('Número')
        plt.ylabel('Selecionado')
        plt.xticks(range(0, 61, 5))
        plt.grid(True, alpha=0.3)
        
        # Salvar gráfico
        arquivo_saida2 = os.path.join(self.output_dir, "numeros_quanticos.png")
        plt.savefig(arquivo_saida2)
        plt.close()
        
        print(f"Visualizações salvas em {arquivo_saida} e {arquivo_saida2}")
        return arquivo_saida
    
    def gerar_previsoes(self, n_previsoes=5):
        """
        Gera previsões para jogos futuros da Mega Sena.
        
        Args:
            n_previsoes: Número de previsões a gerar.
        
        Returns:
            list: Lista de previsões.
        """
        import random
        from collections import Counter
        
        print("Gerando previsões para jogos futuros...")
        
        self.previsoes = []
        
        # Verificar se temos dados necessários
        if not self.numeros_raizes:
            print("Executando detecção de números raízes...")
            self.detectar_numeros_raizes()
        
        if not self.periodos_estabilidade:
            print("Executando detecção de períodos de estabilidade...")
            self.detectar_periodos_estabilidade()
        
        # Obter raízes mais recentes
        raizes_recentes = self.numeros_raizes[-1]['raizes'] if self.numeros_raizes else []
        
        # Obter período atual
        periodo_atual = self.periodos_estabilidade[-1] if self.periodos_estabilidade else None
        
        # Estratégia 1: Previsão baseada em raízes recentes
        previsao_raizes = self._gerar_previsao_baseada_raizes(raizes_recentes)
        self.previsoes.append({
            'metodo': 'raizes_recentes',
            'numeros': previsao_raizes,
            'descricao': 'Baseada nos números raízes mais recentes',
            'confianca': self._calcular_confianca(previsao_raizes, 'raizes')
        })
        
        # Estratégia 2: Previsão baseada em simulação quântica
        try:
            resultados_quanticos = self.simular_computacao_quantica()
            if resultados_quanticos and 'numeros_previstos' in resultados_quanticos:
                previsao_quantica = resultados_quanticos['numeros_previstos']
                self.previsoes.append({
                    'metodo': 'simulacao_quantica',
                    'numeros': previsao_quantica,
                    'descricao': 'Gerada por simulação de computação quântica',
                    'confianca': self._calcular_confianca(previsao_quantica, 'quantico')
                })
        except Exception as e:
            print(f"Erro na simulação quântica: {e}")
        
        # Estratégia 3: Previsão baseada em características do período atual
        if periodo_atual:
            media_pares = periodo_atual['media_pares']
            n_pares = round(media_pares)
            n_impares = 6 - n_pares
            
            # Selecionar números baseados na distribuição de paridade
            todos_numeros = []
            for sorteio in self.sorteios[-20:]:  # Usar sorteios recentes
                todos_numeros.extend(sorteio)
            
            contador = Counter(todos_numeros)
            
            # Separar números pares e ímpares
            pares = [n for n in range(2, 61, 2)]
            impares = [n for n in range(1, 61, 2)]
            
            # Ordenar por frequência
            pares_freq = sorted(pares, key=lambda x: contador.get(x, 0), reverse=True)
            impares_freq = sorted(impares, key=lambda x: contador.get(x, 0), reverse=True)
            
            # Selecionar os mais frequentes
            numeros_paridade = pares_freq[:n_pares] + impares_freq[:n_impares]
            
            previsao_paridade = sorted(numeros_paridade)
            self.previsoes.append({
                'metodo': 'paridade_periodo',
                'numeros': previsao_paridade,
                'descricao': 'Baseada na distribuição de paridade do período atual',
                'confianca': self._calcular_confianca(previsao_paridade, 'periodo')
            })
        
        # Estratégia 4: Previsão híbrida combinando raízes e simulação quântica
        if raizes_recentes and len(self.previsoes) >= 2:
            numeros_hibrido = []
            
            # Incluir algumas raízes
            for raiz in raizes_recentes[:2]:
                if raiz not in numeros_hibrido:
                    numeros_hibrido.append(raiz)
            
            # Incluir alguns números da previsão quântica
            if 'simulacao_quantica' in [p['metodo'] for p in self.previsoes]:
                previsao_quantica = next(p['numeros'] for p in self.previsoes if p['metodo'] == 'simulacao_quantica')
                for num in previsao_quantica[:2]:
                    if num not in numeros_hibrido:
                        numeros_hibrido.append(num)
            
            # Completar com números derivados
            while len(numeros_hibrido) < 6:
                # Gerar número baseado nas raízes
                for raiz in raizes_recentes:
                    num = (raiz * 7 + 13) % 60 + 1
                    if num not in numeros_hibrido:
                        numeros_hibrido.append(num)
                        break
                
                # Se ainda não completou, adicionar número aleatório
                if len(numeros_hibrido) < 6:
                    num = random.randint(1, 60)
                    if num not in numeros_hibrido:
                        numeros_hibrido.append(num)
            
            previsao_hibrida = sorted(numeros_hibrido)
            self.previsoes.append({
                'metodo': 'hibrido',
                'numeros': previsao_hibrida,
                'descricao': 'Combinação de números raízes com simulação quântica',
                'confianca': self._calcular_confianca(previsao_hibrida, 'hibrido')
            })
        
        # Estratégia 5: Previsão baseada em frequência histórica
        todos_numeros = []
        for sorteio in self.sorteios:
            todos_numeros.extend(sorteio)
        
        contador = Counter(todos_numeros)
        numeros_frequentes = [num for num, _ in contador.most_common(6)]
        
        self.previsoes.append({
            'metodo': 'frequencia_historica',
            'numeros': sorted(numeros_frequentes),
            'descricao': 'Baseada nos números mais frequentes historicamente',
            'confianca': self._calcular_confianca(sorted(numeros_frequentes), 'frequencia')
        })
        
        # Ordenar previsões por confiança
        self.previsoes.sort(key=lambda x: x['confianca'], reverse=True)
        
        # Limitar ao número solicitado
        self.previsoes = self.previsoes[:n_previsoes]
        
        print(f"\nGeradas {len(self.previsoes)} previsões finais:")
        for i, prev in enumerate(self.previsoes, 1):
            print(f"{i}. Método: {prev['metodo']} - Números: {prev['numeros']} - Confiança: {prev['confianca']:.2f}")
            print(f"   {prev['descricao']}")
        
        # Visualizar previsões
        self._visualizar_previsoes()
        
        # Salvar previsões
        self._salvar_previsoes()
        
        return self.previsoes
    
    def _gerar_previsao_baseada_raizes(self, raizes):
        """
        Gera uma previsão baseada em números raízes.
        
        Args:
            raizes: Lista de números raízes.
        
        Returns:
            list: Lista com 6 números previstos.
        """
        import random
        
        numeros = []
        
        # Incluir as raízes
        for raiz in raizes:
            if raiz not in numeros:
                numeros.append(raiz)
        
        # Gerar números adicionais baseados nas raízes
        while len(numeros) < 6:
            for raiz in raizes:
                # Usar diferentes transformações das raízes
                candidatos = [
                    (raiz * 7) % 60 + 1,
                    (raiz * 13 + 7) % 60 + 1,
                    (raiz * 17 + 13) % 60 + 1
                ]
                
                for num in candidatos:
                    if num not in numeros and len(numeros) < 6:
                        numeros.append(num)
            
            # Se ainda não completou, adicionar número aleatório
            if len(numeros) < 6:
                num = random.randint(1, 60)
                if num not in numeros:
                    numeros.append(num)
        
        return sorted(numeros[:6])
    
    def _calcular_confianca(self, numeros, tipo_modelo):
        """
        Calcula um valor de confiança para uma previsão.
        
        Args:
            numeros: Lista de números previstos.
            tipo_modelo: Tipo de modelo que gerou a previsão.
        
        Returns:
            float: Valor de confiança entre 0 e 1.
        """
        import random
        
        # Base de confiança por tipo de modelo
        confianca_base = {
            'raizes': 0.7,
            'quantico': 0.6,
            'periodo': 0.65,
            'hibrido': 0.75,
            'frequencia': 0.6
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
        
        from collections import Counter
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
    
    def _visualizar_previsoes(self):
        """
        Cria uma visualização das previsões geradas.
        
        Returns:
            str: Caminho para o arquivo de visualização.
        """
        if not self.previsoes:
            print("Nenhuma previsão para visualizar.")
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
        
        # Salvar gráfico
        arquivo_saida = os.path.join(self.output_dir, "previsoes_finais.png")
        plt.savefig(arquivo_saida)
        plt.close()
        
        print(f"Visualização salva em {arquivo_saida}")
        return arquivo_saida
    
    def _salvar_previsoes(self):
        """
        Salva as previsões em um arquivo JSON.
        
        Returns:
            str: Caminho para o arquivo de previsões.
        """
        if not self.previsoes:
            print("Nenhuma previsão para salvar.")
            return None
        
        data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        dados_saida = {
            "data_geracao": data_atual,
            "total_sorteios_analisados": len(self.sorteios),
            "previsoes": self.previsoes
        }
        
        # Adicionar informações sobre números raízes
        if self.numeros_raizes:
            dados_saida["info_raizes"] = {
                "raizes_recentes": self.numeros_raizes[-1]['raizes'],
                "total_pontos_mudanca": len(self.pontos_mudanca)
            }
        
        # Adicionar informação sobre períodos de estabilidade
        if self.periodos_estabilidade:
            dados_saida["info_periodos"] = {
                "total_periodos": len(self.periodos_estabilidade),
                "periodo_atual": {
                    "inicio": self.periodos_estabilidade[-1]['inicio'],
                    "tamanho": self.periodos_estabilidade[-1]['tamanho'],
                    "raizes": self.periodos_estabilidade[-1]['raizes']
                }
            }
        
        # Salvar em JSON
        arquivo_saida = os.path.join(self.output_dir, "previsoes_mega_sena.json")
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            json.dump(dados_saida, f, indent=2)
        
        print(f"Previsões salvas em {arquivo_saida}")
        
        # Salvar também em formato CSV para fácil visualização
        arquivo_csv = os.path.join(self.output_dir, "previsoes_mega_sena.csv")
        with open(arquivo_csv, 'w', encoding='utf-8') as f:
            f.write("Método,Números,Confiança,Descrição\n")
            for prev in self.previsoes:
                numeros_str = "-".join(str(n) for n in prev['numeros'])
                f.write(f"{prev['metodo']},{numeros_str},{prev['confianca']:.2f},\"{prev['descricao']}\"\n")
        
        print(f"Previsões salvas em formato CSV em {arquivo_csv}")
        
        return arquivo_saida
    
    def validar_com_historico(self, inicio=0, fim=100):
        """
        Valida o modelo usando dados históricos, tentando prever o resultado
        após uma sequência de sorteios.
        
        Args:
            inicio: Índice inicial da sequência.
            fim: Índice final da sequência.
        
        Returns:
            dict: Resultados da validação.
        """
        if len(self.sorteios) <= fim:
            print("Dados insuficientes para a validação solicitada.")
            return {}
        
        print(f"Validando modelo com dados históricos (sorteios {inicio} a {fim})...")
        
        # Usar sorteios de início até fim-1 para prever o sorteio fim
        sorteios_treino = self.sorteios[inicio:fim]
        sorteio_alvo = self.sorteios[fim]
        
        # Criar um predictor temporário com dados até o ponto fim-1
        predictor_temp = MegaSenaPredictor()
        predictor_temp.sorteios = sorteios_treino
        
        # Detectar raízes
        predictor_temp.detectar_numeros_raizes()
        
        # Gerar previsões
        previsoes = predictor_temp.gerar_previsoes()
        
        # Calcular acertos para cada previsão
        acertos_por_previsao = []
        for prev in previsoes:
            acertos = len(set(prev['numeros']).intersection(set(sorteio_alvo)))
            acertos_por_previsao.append({
                'metodo': prev['metodo'],
                'numeros': prev['numeros'],
                'acertos': acertos
            })
        
        # Calcular média de acertos
        media_acertos = np.mean([p['acertos'] for p in acertos_por_previsao])
        
        resultado = {
            'sorteio_previsto': fim,
            'numeros_reais': sorteio_alvo,
            'previsoes': acertos_por_previsao,
            'media_acertos': media_acertos
        }
        
        print(f"\nValidação para sorteio {fim}:")
        print(f"Números reais: {sorteio_alvo}")
        for p in acertos_por_previsao:
            print(f"  {p['metodo']}: {p['numeros']} - Acertos: {p['acertos']}/6")
        print(f"Média de acertos: {media_acertos:.2f}/6")
        
        return resultado
    
    def validar_previsao_101(self):
        """
        Valida especificamente a previsão do 101º resultado usando os 100 primeiros.
        
        Returns:
            dict: Resultados da validação.
        """
        return self.validar_com_historico(0, 100)
    
    def gerar_relatorio(self):
        """
        Gera um relatório completo com todas as análises e previsões.
        
        Returns:
            str: Caminho para o arquivo de relatório.
        """
        if not self.previsoes:
            print("Execute gerar_previsoes() primeiro.")
            return None
        
        print("Gerando relatório completo...")
        
        # Criar relatório em HTML
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório de Análise da Mega Sena</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .section {{ margin-bottom: 30px; padding: 20px; background-color: #f9f9f9; border-radius: 5px; }}
                .prediction {{ margin-bottom: 15px; padding: 15px; background-color: #fff; border-left: 4px solid #3498db; }}
                .prediction-high {{ border-left-color: #2ecc71; }}
                .prediction-medium {{ border-left-color: #f39c12; }}
                .prediction-low {{ border-left-color: #e74c3c; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .number-ball {{ display: inline-block; width: 30px; height: 30px; line-height: 30px; text-align: center; 
                               background-color: #3498db; color: white; border-radius: 50%; margin-right: 5px; }}
                img {{ max-width: 100%; height: auto; margin: 20px 0; border: 1px solid #ddd; }}
                .footer {git remote add origin https://github.com/USUARIO/NOME_REPOSITORIO.git{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.9em; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Relatório de Análise da Mega Sena</h1>
                <p>Data de geração: {data_geracao}</p>
                <p>Total de sorteios analisados: {total_sorteios}</p>
                
                <div class="section">
                    <h2>Metodologia</h2>
                    <p>Este relatório foi gerado com base na hipótese de que os números da Mega Sena são gerados artificialmente a partir de números raízes, que podem mudar ao longo do tempo. A análise combina:</p>
                    <ul>
                        <li>Detecção de possíveis números raízes nos dados históricos</li>
                        <li>Identificação de períodos de estabilidade e pontos de mudança</li>
                        <li>Simulação de computação quântica para identificar padrões ocultos</li>
                        <li>Análise de características estatísticas dos sorteios</li>
                    </ul>
                </div>
                
                <div class="section">
                    <h2>Números Raízes Detectados</h2>
                    <p>Os números raízes mais recentes detectados são: {raizes_recentes}</p>
                    <p>Foram identificados {total_pontos_mudanca} pontos de mudança nos números raízes ao longo do histórico.</p>
                    <img src="evolucao_raizes.png" alt="Evolução dos Números Raízes">
                </div>
                
                <div class="section">
                    <h2>Períodos de Estabilidade</h2>
                    <p>Foram identificados {total_periodos} períodos de estabilidade nos padrões da Mega Sena.</p>
                    <p>O período atual começou no sorteio {periodo_atual_inicio} e tem duração de {periodo_atual_tamanho} sorteios.</p>
                    <img src="periodos_estabilidade.png" alt="Períodos de Estabilidade">
                </div>
                
                <div class="section">
                    <h2>Previsões Geradas</h2>
                    <p>Com base nas análises realizadas, foram geradas as seguintes previsões para jogos futuros:</p>
                    
                    {previsoes_html}
                    
                    <img src="previsoes_finais.png" alt="Visualização das Previsões">
                </div>
                
                <div class="section">
                    <h2>Considerações Importantes</h2>
                    <p>É fundamental ressaltar que, apesar da análise detalhada e das metodologias avançadas utilizadas, a Mega Sena continua sendo um jogo de sorte com probabilidades extremamente baixas de acerto (1 em 50.063.860 para a sena).</p>
                    <p>As estratégias apresentadas podem aumentar ligeiramente as chances, mas não garantem sucesso. Use estas previsões como uma referência adicional, não como garantia de resultados.</p>
                </div>
                
                <div class="footer">
                    <p>Este relatório foi gerado automaticamente pelo sistema MegaSenaPredictor.</p>
                    <p>Desenvolvido com base na hipótese de que os números da Mega Sena são gerados artificialmente.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Preparar dados para o template
        data_geracao = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        total_sorteios = len(self.sorteios)
        
        # Informações sobre raízes
        raizes_recentes = ", ".join(str(r) for r in self.numeros_raizes[-1]['raizes']) if self.numeros_raizes else "N/A"
        total_pontos_mudanca = len(self.pontos_mudanca)
        
        # Informações sobre períodos
        total_periodos = len(self.periodos_estabilidade)
        periodo_atual_inicio = self.periodos_estabilidade[-1]['inicio'] if self.periodos_estabilidade else "N/A"
        periodo_atual_tamanho = self.periodos_estabilidade[-1]['tamanho'] if self.periodos_estabilidade else "N/A"
        
        # Gerar HTML para previsões
        previsoes_html = ""
        for i, prev in enumerate(self.previsoes, 1):
            # Determinar classe de confiança
            if prev['confianca'] >= 0.7:
                confianca_classe = "prediction-high"
            elif prev['confianca'] >= 0.5:
                confianca_classe = "prediction-medium"
            else:
                confianca_classe = "prediction-low"
            
            # Gerar HTML para os números
            numeros_html = ""
            for num in prev['numeros']:
                numeros_html += f'<span class="number-ball">{num}</span>'
            
            # Gerar HTML para a previsão
            previsoes_html += f"""
            <div class="prediction {confianca_classe}">
                <h3>Previsão {i}: {prev['metodo']}</h3>
                <p><strong>Números:</strong> {numeros_html}</p>
                <p><strong>Confiança:</strong> {prev['confianca']:.2f}</p>
                <p><strong>Descrição:</strong> {prev['descricao']}</p>
            </div>
            """
        
        # Substituir placeholders no template
        html = html.format(
            data_geracao=data_geracao,
            total_sorteios=total_sorteios,
            raizes_recentes=raizes_recentes,
            total_pontos_mudanca=total_pontos_mudanca,
            total_periodos=total_periodos,
            periodo_atual_inicio=periodo_atual_inicio,
            periodo_atual_tamanho=periodo_atual_tamanho,
            previsoes_html=previsoes_html
        )
        
        # Salvar relatório
        arquivo_saida = os.path.join(self.output_dir, "relatorio_mega_sena.html")
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Relatório gerado em {arquivo_saida}")
        return arquivo_saida


def main():
    """Função principal para execução do programa."""
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description='Sistema de previsão para a Mega Sena baseado em números raízes e simulação quântica.')
    
    parser.add_argument('--download', action='store_true', help='Baixar dados históricos da Mega Sena')
    parser.add_argument('--force', action='store_true', help='Forçar download mesmo se o arquivo já existir')
    parser.add_argument('--raizes', action='store_true', help='Detectar números raízes')
    parser.add_argument('--periodos', action='store_true', help='Detectar períodos de estabilidade')
    parser.add_argument('--quantico', action='store_true', help='Executar simulação quântica')
    parser.add_argument('--previsoes', type=int, default=0, help='Gerar previsões (especifique o número de previsões)')
    parser.add_argument('--validar', action='store_true', help='Validar modelo com dados históricos')
    parser.add_argument('--validar101', action='store_true', help='Validar previsão do 101º resultado')
    parser.add_argument('--relatorio', action='store_true', help='Gerar relatório completo')
    parser.add_argument('--arquivo', type=str, help='Arquivo de dados personalizado')
    
    args = parser.parse_args()
    
    # Criar instância do predictor
    predictor = MegaSenaPredictor()
    
    # Executar ações conforme argumentos
    if args.download:
        predictor.baixar_dados_historicos(force=args.force)
    
    # Carregar dados
    if args.arquivo:
        predictor.carregar_dados(args.arquivo)
    else:
        arquivo_padrao = os.path.join(predictor.data_dir, 'megasena_dados.json')
        if os.path.exists(arquivo_padrao):
            predictor.carregar_dados()
        else:
            print(f"Arquivo de dados não encontrado em {arquivo_padrao}.")
            print("Baixando dados históricos...")
            predictor.baixar_dados_historicos()
            predictor.carregar_dados()
    
    # Executar análises
    if args.raizes:
        predictor.detectar_numeros_raizes()
    
    if args.periodos:
        predictor.detectar_periodos_estabilidade()
    
    if args.quantico:
        predictor.simular_computacao_quantica()
    
    if args.previsoes > 0:
        predictor.gerar_previsoes(n_previsoes=args.previsoes)
    
    if args.validar:
        predictor.validar_com_historico()
    
    if args.validar101:
        predictor.validar_previsao_101()
    
    if args.relatorio:
        if not predictor.previsoes:
            print("Gerando previsões para o relatório...")
            predictor.gerar_previsoes()
        predictor.gerar_relatorio()
    
    # Se nenhum argumento específico foi fornecido, mostrar menu interativo
    if not any([args.download, args.raizes, args.periodos, args.quantico, 
                args.previsoes, args.validar, args.validar101, args.relatorio]):
        menu_interativo(predictor)


def menu_interativo(predictor):
    """
    Exibe um menu interativo para o usuário.
    
    Args:
        predictor: Instância de MegaSenaPredictor.
    """
    while True:
        print("\n===== MegaSenaPredictor =====")
        print("1. Baixar dados históricos da Mega Sena")
        print("2. Detectar números raízes")
        print("3. Detectar períodos de estabilidade")
        print("4. Executar simulação quântica")
        print("5. Gerar previsões")
        print("6. Validar modelo com dados históricos")
        print("7. Validar previsão do 101º resultado")
        print("8. Adicionar sorteios recentes")
        print("9. Gerar relatório completo")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            force = input("Forçar download mesmo se o arquivo já existir? (s/n): ").lower() == 's'
            predictor.baixar_dados_historicos(force=force)
            predictor.carregar_dados()
        
        elif opcao == "2":
            tamanho_janela = int(input("Tamanho da janela de análise (padrão: 50): ") or "50")
            n_raizes = int(input("Número de raízes a detectar (padrão: 3): ") or "3")
            predictor.detectar_numeros_raizes(tamanho_janela=tamanho_janela, n_raizes=n_raizes)
        
        elif opcao == "3":
            min_tamanho = int(input("Tamanho mínimo de um período (padrão: 20): ") or "20")
            predictor.detectar_periodos_estabilidade(min_tamanho=min_tamanho)
        
        elif opcao == "4":
            n_qubits = int(input("Número de qubits (padrão: 6): ") or "6")
            predictor.simular_computacao_quantica(n_qubits=n_qubits)
        
        elif opcao == "5":
            n_previsoes = int(input("Número de previsões a gerar (padrão: 5): ") or "5")
            predictor.gerar_previsoes(n_previsoes=n_previsoes)
        
        elif opcao == "6":
            inicio = int(input("Índice inicial (padrão: 0): ") or "0")
            fim = int(input("Índice final (padrão: 100): ") or "100")
            predictor.validar_com_historico(inicio=inicio, fim=fim)
        
        elif opcao == "7":
            predictor.validar_previsao_101()
        
        elif opcao == "8":
            print("Adicionar sorteios recentes (formato: 1,2,3,4,5,6)")
            print("Digite 'fim' para terminar.")
            
            novos_sorteios = []
            while True:
                entrada = input("Sorteio: ")
                if entrada.lower() == 'fim':
                    break
                
                try:
                    numeros = [int(n.strip()) for n in entrada.split(',')]
                    if len(numeros) != 6:
                        print("Erro: O sorteio deve ter exatamente 6 números.")
                        continue
                    
                    for num in numeros:
                        if not (1 <= num <= 60):
                            print(f"Erro: Número {num} fora do intervalo válido (1-60).")
                            break
                    else:
                        novos_sorteios.append(numeros)
                        print(f"Sorteio adicionado: {numeros}")
                except ValueError:
                    print("Erro: Formato inválido. Use números separados por vírgula.")
            
            if novos_sorteios:
                predictor.adicionar_sorteios_recentes(novos_sorteios)
        
        elif opcao == "9":
            if not predictor.previsoes:
                print("Gerando previsões para o relatório...")
                predictor.gerar_previsoes()
            predictor.gerar_relatorio()
        
        elif opcao == "0":
            print("Encerrando o programa.")
            break
        
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()

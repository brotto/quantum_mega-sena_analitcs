import numpy as np
import matplotlib.pyplot as plt
import json
import os
from collections import Counter
import pennylane as qml
import random
import datetime

class DetectorNumerosRaizes:
    """
    Classe para detectar possíveis números raízes que poderiam estar gerando
    os resultados da Mega Sena, assumindo que são gerados artificialmente.
    """
    
    def __init__(self):
        """Inicializa o detector de números raízes."""
        self.dados_historicos = {}
        self.sorteios = []
        self.janelas_analise = []
        self.numeros_raizes = []
        self.pontos_mudanca = []
    
    def carregar_dados(self, arquivo_json):
        """
        Carrega os dados históricos da Mega Sena de um arquivo JSON.
        
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
            return True
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return False
    
    def analisar_janelas_temporais(self, tamanho_janela=50, sobreposicao=0.5):
        """
        Analisa os dados em janelas temporais para detectar possíveis mudanças nos números raízes.
        
        Args:
            tamanho_janela: Tamanho de cada janela de análise.
            sobreposicao: Proporção de sobreposição entre janelas consecutivas.
        
        Returns:
            list: Lista de janelas de análise.
        """
        if not self.sorteios:
            print("Nenhum dado carregado para análise.")
            return []
        
        # Calcular o passo entre janelas
        passo = int(tamanho_janela * (1 - sobreposicao))
        if passo < 1:
            passo = 1
        
        # Criar janelas de análise
        self.janelas_analise = []
        for i in range(0, len(self.sorteios) - tamanho_janela + 1, passo):
            janela = {
                'inicio': i,
                'fim': i + tamanho_janela,
                'sorteios': self.sorteios[i:i + tamanho_janela]
            }
            self.janelas_analise.append(janela)
        
        print(f"Criadas {len(self.janelas_analise)} janelas de análise.")
        return self.janelas_analise
    
    def detectar_numeros_raizes(self, n_raizes=3):
        """
        Detecta possíveis números raízes para cada janela de análise.
        
        Args:
            n_raizes: Número de raízes a detectar por janela.
        
        Returns:
            list: Lista de números raízes detectados para cada janela.
        """
        if not self.janelas_analise:
            print("Execute analisar_janelas_temporais() primeiro.")
            return []
        
        self.numeros_raizes = []
        
        for idx, janela in enumerate(self.janelas_analise):
            # Extrair características da janela
            raizes = self._extrair_raizes_da_janela(janela['sorteios'], n_raizes)
            
            self.numeros_raizes.append({
                'janela_idx': idx,
                'inicio': janela['inicio'],
                'fim': janela['fim'],
                'raizes': raizes
            })
        
        print(f"Detectados números raízes para {len(self.numeros_raizes)} janelas.")
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
    
    def detectar_pontos_mudanca(self, limiar_diferenca=0.5):
        """
        Detecta pontos onde os números raízes parecem mudar significativamente.
        
        Args:
            limiar_diferenca: Limiar para considerar uma mudança significativa.
        
        Returns:
            list: Lista de índices onde ocorreram mudanças significativas.
        """
        if not self.numeros_raizes:
            print("Execute detectar_numeros_raizes() primeiro.")
            return []
        
        self.pontos_mudanca = []
        
        for i in range(1, len(self.numeros_raizes)):
            raizes_atuais = set(self.numeros_raizes[i]['raizes'])
            raizes_anteriores = set(self.numeros_raizes[i-1]['raizes'])
            
            # Calcular diferença como proporção de números diferentes
            diferenca = 1 - len(raizes_atuais.intersection(raizes_anteriores)) / len(raizes_atuais)
            
            if diferenca >= limiar_diferenca:
                self.pontos_mudanca.append({
                    'janela_idx': i,
                    'inicio_sorteio': self.numeros_raizes[i]['inicio'],
                    'diferenca': diferenca,
                    'raizes_antes': self.numeros_raizes[i-1]['raizes'],
                    'raizes_depois': self.numeros_raizes[i]['raizes']
                })
        
        print(f"Detectados {len(self.pontos_mudanca)} pontos de mudança nos números raízes.")
        return self.pontos_mudanca
    
    def visualizar_evolucao_raizes(self, arquivo_saida="evolucao_raizes.png"):
        """
        Cria uma visualização da evolução dos números raízes ao longo do tempo.
        
        Args:
            arquivo_saida: Nome do arquivo para salvar a visualização.
        
        Returns:
            str: Caminho para o arquivo de visualização.
        """
        if not self.numeros_raizes:
            print("Execute detectar_numeros_raizes() primeiro.")
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
        
        plt.savefig(arquivo_saida)
        plt.close()
        
        print(f"Visualização salva em {arquivo_saida}")
        return arquivo_saida


class SimuladorQuantico:
    """
    Classe para implementar simulações quânticas para análise de padrões
    e geração de previsões para a Mega Sena.
    """
    
    def __init__(self, n_qubits=6):
        """
        Inicializa o simulador quântico.
        
        Args:
            n_qubits: Número de qubits a utilizar na simulação.
        """
        self.n_qubits = n_qubits
        self.dev = qml.device("default.qubit", wires=n_qubits)
    
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
    
    def _criar_circuito_grover(self, dados_entrada):
        """
        Cria um circuito quântico baseado no algoritmo de Grover para
        identificar padrões nos dados.
        
        Args:
            dados_entrada: Dados de entrada normalizados.
        
        Returns:
            function: Função do circuito quântico.
        """
        @qml.qnode(self.dev)
        def circuito(params):
            # Preparar estado inicial em superposição
            for i in range(self.n_qubits):
                qml.Hadamard(wires=i)
            
            # Aplicar operações baseadas nos dados
            for i in range(self.n_qubits):
                idx = i % len(dados_entrada)
                qml.RY(np.pi * dados_entrada[idx], wires=i)
            
            # Criar emaranhamento
            for i in range(self.n_qubits - 1):
                qml.CNOT(wires=[i, i+1])
            
            # Aplicar operações de fase baseadas nos parâmetros
            for i in range(self.n_qubits):
                qml.PhaseShift(params[i], wires=i)
            
            # Aplicar operações de Grover
            for _ in range(2):  # Número de iterações de Grover
                # Difusão
                for i in range(self.n_qubits):
                    qml.Hadamard(wires=i)
                    qml.PhaseShift(np.pi, wires=i)
                
                # Emaranhamento
                for i in range(self.n_qubits - 1):
                    qml.CNOT(wires=[i, i+1])
                
                # Desfazer difusão
                for i in range(self.n_qubits):
                    qml.PhaseShift(np.pi, wires=i)
                    qml.Hadamard(wires=i)
            
            # Retornar probabilidades
            return [qml.probs(wires=i) for i in range(self.n_qubits)]
        
        return circuito
    
    def _criar_circuito_qwalk(self, dados_entrada):
        """
        Cria um circuito quântico baseado em caminhada quântica para
        identificar padrões nos dados.
        
        Args:
            dados_entrada: Dados de entrada normalizados.
        
        Returns:
            function: Função do circuito quântico.
        """
        @qml.qnode(self.dev)
        def circuito(params):
            # Preparar estado inicial
            for i in range(self.n_qubits):
                qml.RY(params[i], wires=i)
            
            # Implementar caminhada quântica
            for step in range(3):  # Número de passos da caminhada
                # Aplicar rotações baseadas nos dados
                for i in range(self.n_qubits):
                    idx = (i + step) % len(dados_entrada)
                    qml.RZ(np.pi * dados_entrada[idx], wires=i)
                
                # Criar emaranhamento (moeda quântica)
                for i in range(self.n_qubits):
                    qml.Hadamard(wires=i)
                
                # Operação de deslocamento condicional
                for i in range(self.n_qubits - 1):
                    qml.CNOT(wires=[i, (i+1) % self.n_qubits])
            
            # Retornar probabilidades
            return [qml.probs(wires=i) for i in range(self.n_qubits)]
        
        return circuito
    
    def _converter_para_numeros_mega(self, resultados_quanticos):
        """
        Converte resultados quânticos em números para a Mega Sena.
        
        Args:
            resultados_quanticos: Lista de arrays de probabilidades.
        
        Returns:
            list: Lista de números entre 1 e 60.
        """
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
    
    def gerar_previsao_grover(self, sorteios):
        """
        Gera uma previsão usando o algoritmo de Grover.
        
        Args:
            sorteios: Lista de sorteios para análise.
        
        Returns:
            list: Lista com 6 números previstos.
        """
        # Preparar dados
        dados_entrada = self._preparar_dados_entrada(sorteios)
        
        # Criar circuito
        circuito = self._criar_circuito_grover(dados_entrada)
        
        # Inicializar parâmetros aleatórios
        params = np.random.uniform(0, np.pi, self.n_qubits)
        
        # Executar circuito
        resultados = circuito(params)
        
        # Converter para números da Mega Sena
        return self._converter_para_numeros_mega(resultados)
    
    def gerar_previsao_qwalk(self, sorteios):
        """
        Gera uma previsão usando caminhada quântica.
        
        Args:
            sorteios: Lista de sorteios para análise.
        
        Returns:
            list: Lista com 6 números previstos.
        """
        # Preparar dados
        dados_entrada = self._preparar_dados_entrada(sorteios)
        
        # Criar circuito
        circuito = self._criar_circuito_qwalk(dados_entrada)
        
        # Inicializar parâmetros aleatórios
        params = np.random.uniform(0, np.pi, self.n_qubits)
        
        # Executar circuito
        resultados = circuito(params)
        
        # Converter para números da Mega Sena
        return self._converter_para_numeros_mega(resultados)
    
    def gerar_previsao_hibrida(self, sorteios, raizes):
        """
        Gera uma previsão híbrida combinando simulação quântica com números raízes.
        
        Args:
            sorteios: Lista de sorteios para análise.
            raizes: Lista de números raízes detectados.
        
        Returns:
            list: Lista com 6 números previstos.
        """
        # Gerar previsão com caminhada quântica
        previsao_qwalk = self.gerar_previsao_qwalk(sorteios)
        
        # Usar números raízes para influenciar a previsão
        numeros = []
        
        # Incluir alguns números raízes
        for raiz in raizes[:2]:  # Usar até 2 raízes
            if raiz not in numeros:
                numeros.append(raiz)
        
        # Incluir alguns números da previsão quântica
        for num in previsao_qwalk:
            if num not in numeros and len(numeros) < 6:
                numeros.append(num)
        
        # Completar se necessário
        while len(numeros) < 6:
            # Gerar número baseado nas raízes
            for raiz in raizes:
                num = (raiz * 7 + 13) % 60 + 1
                if num not in numeros:
                    numeros.append(num)
                    break
            
            # Se ainda não completou, adicionar número aleatório
            if len(numeros) < 6:
                num = random.randint(1, 60)
                if num not in numeros:
                    numeros.append(num)
        
        return sorted(numeros[:6])


class GeradorPrevisoes:
    """
    Classe para gerar previsões de jogos da Mega Sena com base em números raízes
    e simulação quântica.
    """
    
    def __init__(self):
        """Inicializa o gerador de previsões."""
        self.detector = DetectorNumerosRaizes()
        self.simulador = SimuladorQuantico()
        self.previsoes = []
    
    def carregar_dados(self, arquivo_json):
        """
        Carrega os dados históricos da Mega Sena.
        
        Args:
            arquivo_json: Caminho para o arquivo JSON com os dados históricos.
        
        Returns:
            bool: True se os dados foram carregados com sucesso, False caso contrário.
        """
        return self.detector.carregar_dados(arquivo_json)
    
    def analisar_dados(self, tamanho_janela=50, n_raizes=3, limiar_mudanca=0.5):
        """
        Realiza a análise completa dos dados para detectar números raízes e pontos de mudança.
        
        Args:
            tamanho_janela: Tamanho da janela de análise.
            n_raizes: Número de raízes a detectar.
            limiar_mudanca: Limiar para detectar mudanças significativas.
        
        Returns:
            dict: Resultados da análise.
        """
        # Analisar janelas temporais
        self.detector.analisar_janelas_temporais(tamanho_janela=tamanho_janela)
        
        # Detectar números raízes
        self.detector.detectar_numeros_raizes(n_raizes=n_raizes)
        
        # Detectar pontos de mudança
        self.detector.detectar_pontos_mudanca(limiar_diferenca=limiar_mudanca)
        
        # Visualizar evolução das raízes
        self.detector.visualizar_evolucao_raizes()
        
        return {
            'numeros_raizes': self.detector.numeros_raizes,
            'pontos_mudanca': self.detector.pontos_mudanca
        }
    
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
        if not self.detector.sorteios or len(self.detector.sorteios) <= fim:
            print("Dados insuficientes para a validação solicitada.")
            return {}
        
        # Usar sorteios de início até fim-1 para prever o sorteio fim
        sorteios_treino = self.detector.sorteios[inicio:fim]
        sorteio_alvo = self.detector.sorteios[fim]
        
        # Detectar raízes na sequência de treino
        janela = {'sorteios': sorteios_treino}
        raizes = self.detector._extrair_raizes_da_janela(sorteios_treino, n_raizes=3)
        
        # Gerar previsões usando diferentes métodos
        previsao_raizes = self._gerar_previsao_baseada_raizes(raizes)
        previsao_grover = self.simulador.gerar_previsao_grover(sorteios_treino[-20:])
        previsao_qwalk = self.simulador.gerar_previsao_qwalk(sorteios_treino[-20:])
        previsao_hibrida = self.simulador.gerar_previsao_hibrida(sorteios_treino[-20:], raizes)
        
        # Calcular acertos para cada método
        acertos_raizes = len(set(previsao_raizes).intersection(set(sorteio_alvo)))
        acertos_grover = len(set(previsao_grover).intersection(set(sorteio_alvo)))
        acertos_qwalk = len(set(previsao_qwalk).intersection(set(sorteio_alvo)))
        acertos_hibrida = len(set(previsao_hibrida).intersection(set(sorteio_alvo)))
        
        resultado = {
            'sorteio_previsto': fim,
            'numeros_reais': sorteio_alvo,
            'raizes_detectadas': raizes,
            'previsoes': {
                'baseada_raizes': {'numeros': previsao_raizes, 'acertos': acertos_raizes},
                'grover': {'numeros': previsao_grover, 'acertos': acertos_grover},
                'qwalk': {'numeros': previsao_qwalk, 'acertos': acertos_qwalk},
                'hibrida': {'numeros': previsao_hibrida, 'acertos': acertos_hibrida}
            }
        }
        
        print(f"\nValidação para sorteio {fim}:")
        print(f"Números reais: {sorteio_alvo}")
        print(f"Raízes detectadas: {raizes}")
        print(f"Previsão baseada em raízes: {previsao_raizes} - Acertos: {acertos_raizes}/6")
        print(f"Previsão Grover: {previsao_grover} - Acertos: {acertos_grover}/6")
        print(f"Previsão Caminhada Quântica: {previsao_qwalk} - Acertos: {acertos_qwalk}/6")
        print(f"Previsão Híbrida: {previsao_hibrida} - Acertos: {acertos_hibrida}/6")
        
        return resultado
    
    def _gerar_previsao_baseada_raizes(self, raizes):
        """
        Gera uma previsão baseada em números raízes.
        
        Args:
            raizes: Lista de números raízes.
        
        Returns:
            list: Lista com 6 números previstos.
        """
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
        
        return sorted(numeros[:6])
    
    def gerar_previsoes_finais(self, n_previsoes=5):
        """
        Gera previsões finais para jogos futuros da Mega Sena.
        
        Args:
            n_previsoes: Número de previsões a gerar.
        
        Returns:
            list: Lista de previsões.
        """
        if not self.detector.sorteios:
            print("Nenhum dado disponível para gerar previsões.")
            return []
        
        # Se não temos números raízes detectados, fazer a análise
        if not self.detector.numeros_raizes:
            self.analisar_dados()
        
        # Usar as raízes mais recentes
        raizes_recentes = self.detector.numeros_raizes[-1]['raizes'] if self.detector.numeros_raizes else [10, 25, 53]
        
        # Usar os sorteios mais recentes para a simulação quântica
        sorteios_recentes = self.detector.sorteios[-20:]
        
        # Gerar previsões usando diferentes métodos
        self.previsoes = []
        
        # 1. Previsão baseada em raízes
        previsao_raizes = self._gerar_previsao_baseada_raizes(raizes_recentes)
        self.previsoes.append({
            'metodo': 'baseada_raizes',
            'numeros': previsao_raizes,
            'descricao': 'Baseada nos números raízes detectados'
        })
        
        # 2. Previsão usando algoritmo de Grover
        previsao_grover = self.simulador.gerar_previsao_grover(sorteios_recentes)
        self.previsoes.append({
            'metodo': 'grover',
            'numeros': previsao_grover,
            'descricao': 'Gerada usando simulação do algoritmo de Grover'
        })
        
        # 3. Previsão usando caminhada quântica
        previsao_qwalk = self.simulador.gerar_previsao_qwalk(sorteios_recentes)
        self.previsoes.append({
            'metodo': 'qwalk',
            'numeros': previsao_qwalk,
            'descricao': 'Gerada usando simulação de caminhada quântica'
        })
        
        # 4. Previsão híbrida
        previsao_hibrida = self.simulador.gerar_previsao_hibrida(sorteios_recentes, raizes_recentes)
        self.previsoes.append({
            'metodo': 'hibrida',
            'numeros': previsao_hibrida,
            'descricao': 'Combinação de simulação quântica com números raízes'
        })
        
        # 5. Previsão com variação temporal
        if len(self.detector.pontos_mudanca) > 0:
            # Usar informação sobre mudanças temporais
            ultimo_ponto = self.detector.pontos_mudanca[-1]
            raizes_antes = ultimo_ponto['raizes_antes']
            raizes_depois = ultimo_ponto['raizes_depois']
            
            # Combinar raízes de antes e depois da mudança
            raizes_combinadas = list(set(raizes_antes + raizes_depois))[:3]
            
            previsao_temporal = self._gerar_previsao_baseada_raizes(raizes_combinadas)
            self.previsoes.append({
                'metodo': 'temporal',
                'numeros': previsao_temporal,
                'descricao': 'Baseada em mudanças temporais nos números raízes'
            })
        
        # Limitar ao número solicitado
        self.previsoes = self.previsoes[:n_previsoes]
        
        print(f"\nGeradas {len(self.previsoes)} previsões finais:")
        for i, prev in enumerate(self.previsoes, 1):
            print(f"{i}. Método: {prev['metodo']} - Números: {prev['numeros']}")
            print(f"   {prev['descricao']}")
        
        return self.previsoes
    
    def salvar_previsoes(self, arquivo="previsoes_mega_sena.json"):
        """
        Salva as previsões em um arquivo JSON.
        
        Args:
            arquivo: Nome do arquivo para salvar.
        
        Returns:
            bool: True se as previsões foram salvas com sucesso, False caso contrário.
        """
        if not self.previsoes:
            print("Nenhuma previsão para salvar. Execute gerar_previsoes_finais() primeiro.")
            return False
        
        try:
            data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            dados_saida = {
                "data_geracao": data_atual,
                "total_sorteios_analisados": len(self.detector.sorteios),
                "previsoes": self.previsoes
            }
            
            # Adicionar informações sobre números raízes se disponíveis
            if self.detector.numeros_raizes:
                dados_saida["info_raizes"] = {
                    "total_janelas": len(self.detector.numeros_raizes),
                    "raizes_recentes": self.detector.numeros_raizes[-1]['raizes'],
                    "total_pontos_mudanca": len(self.detector.pontos_mudanca)
                }
            
            with open(arquivo, 'w') as f:
                json.dump(dados_saida, f, indent=2)
            
            print(f"Previsões salvas com sucesso em {arquivo}")
            return True
        except Exception as e:
            print(f"Erro ao salvar previsões: {e}")
            return False


def main():
    """Função principal para execução do programa."""
    print("\n===== Análise de Números Raízes da Mega Sena =====")
    print("Baseado na hipótese de que os números são gerados artificialmente")
    print("====================================================\n")
    
    gerador = GeradorPrevisoes()
    
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
        print("1. Analisar dados e detectar números raízes")
        print("2. Validar com histórico (prever o 101º resultado usando os 100 primeiros)")
        print("3. Gerar previsões para jogos futuros")
        print("4. Personalizar validação histórica")
        print("5. Salvar previsões")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            tamanho = int(input("Tamanho da janela para análise (padrão: 50): ") or "50")
            n_raizes = int(input("Número de raízes a detectar (padrão: 3): ") or "3")
            limiar = float(input("Limiar para detectar mudanças (padrão: 0.5): ") or "0.5")
            
            gerador.analisar_dados(tamanho_janela=tamanho, n_raizes=n_raizes, limiar_mudanca=limiar)
        
        elif opcao == "2":
            gerador.validar_com_historico(0, 100)
        
        elif opcao == "3":
            n_previsoes = int(input("Número de previsões a gerar (padrão: 5): ") or "5")
            gerador.gerar_previsoes_finais(n_previsoes=n_previsoes)
        
        elif opcao == "4":
            inicio = int(input("Índice inicial (padrão: 0): ") or "0")
            fim = int(input("Índice final (padrão: 100): ") or "100")
            gerador.validar_com_historico(inicio, fim)
        
        elif opcao == "5":
            if not gerador.previsoes:
                print("Nenhuma previsão gerada. Execute a opção 3 primeiro.")
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

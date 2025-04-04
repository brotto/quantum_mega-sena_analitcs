import numpy as np
import json
import matplotlib.pyplot as plt
from collections import Counter
import pennylane as qml
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import random
import os
import datetime

class AnalisadorMegaSena:
    """
    Classe para análise de números da Mega Sena sob a hipótese de que são gerados
    artificialmente a partir de números raízes.
    """
    
    def __init__(self, arquivo_dados=None):
        """
        Inicializa o analisador.
        
        Args:
            arquivo_dados: Caminho para o arquivo JSON com os dados históricos.
                          Se None, tentará carregar de um caminho padrão.
        """
        self.dados_historicos = None
        self.sorteios = []
        self.numeros_raizes = []
        self.periodos_mudanca = []
        self.modelo_treinado = False
        
        # Carregar dados se o arquivo for fornecido
        if arquivo_dados:
            self.carregar_dados(arquivo_dados)
    
    def carregar_dados(self, arquivo):
        """
        Carrega dados históricos da Mega Sena de um arquivo JSON.
        
        Args:
            arquivo: Caminho para o arquivo JSON.
        
        Returns:
            bool: True se os dados foram carregados com sucesso, False caso contrário.
        """
        try:
            with open(arquivo, 'r') as f:
                self.dados_historicos = json.load(f)
            
            # Converter para lista de listas de inteiros
            self.sorteios = []
            for concurso, numeros in sorted(self.dados_historicos.items(), key=lambda x: int(x[0])):
                self.sorteios.append([int(n) for n in numeros])
            
            print(f"Dados carregados com sucesso: {len(self.sorteios)} sorteios.")
            return True
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return False
    
    def adicionar_novos_sorteios(self, novos_sorteios):
        """
        Adiciona novos sorteios aos dados históricos.
        
        Args:
            novos_sorteios: Lista de listas, onde cada lista interna contém 6 números de um sorteio.
        """
        if not self.sorteios:
            self.sorteios = novos_sorteios
        else:
            self.sorteios.extend(novos_sorteios)
        
        print(f"Adicionados {len(novos_sorteios)} novos sorteios. Total: {len(self.sorteios)}")
    
    def detectar_numeros_raizes(self, tamanho_janela=100, n_raizes=3):
        """
        Detecta possíveis números raízes que poderiam estar gerando os resultados.
        
        Args:
            tamanho_janela: Tamanho da janela deslizante para análise.
            n_raizes: Número de raízes a detectar.
        
        Returns:
            List: Lista de tuplas (índice_início, números_raízes).
        """
        if not self.sorteios:
            print("Nenhum dado carregado para análise.")
            return []
        
        self.numeros_raizes = []
        self.periodos_mudanca = []
        
        # Usar janela deslizante para detectar mudanças nos números raízes
        for i in range(0, len(self.sorteios) - tamanho_janela, tamanho_janela // 2):
            janela = self.sorteios[i:i+tamanho_janela]
            raizes = self._encontrar_raizes_em_janela(janela, n_raizes)
            self.numeros_raizes.append((i, raizes))
            
            # Detectar mudanças significativas nas raízes
            if len(self.numeros_raizes) > 1:
                raizes_anteriores = self.numeros_raizes[-2][1]
                if self._calcular_diferenca_raizes(raizes, raizes_anteriores) > 0.3:
                    self.periodos_mudanca.append(i)
        
        print(f"Detectados {len(self.numeros_raizes)} conjuntos de números raízes.")
        print(f"Detectadas {len(self.periodos_mudanca)} possíveis mudanças nos números raízes.")
        
        return self.numeros_raizes
    
    def _encontrar_raizes_em_janela(self, janela, n_raizes):
        """
        Encontra possíveis números raízes em uma janela de sorteios.
        
        Args:
            janela: Lista de sorteios.
            n_raizes: Número de raízes a encontrar.
        
        Returns:
            List: Lista de números raízes.
        """
        # Abordagem 1: Análise de frequência
        todos_numeros = []
        for sorteio in janela:
            todos_numeros.extend(sorteio)
        
        contador = Counter(todos_numeros)
        numeros_frequentes = [num for num, _ in contador.most_common(10)]
        
        # Abordagem 2: Análise de padrões de paridade
        padroes_paridade = []
        for sorteio in janela:
            pares = sum(1 for n in sorteio if n % 2 == 0)
            impares = 6 - pares
            padroes_paridade.append((pares, impares))
        
        padrao_comum = Counter(padroes_paridade).most_common(1)[0][0]
        
        # Abordagem 3: Análise de soma dos números
        somas = [sum(sorteio) for sorteio in janela]
        soma_media = int(np.mean(somas))
        
        # Combinar as abordagens para gerar números raízes
        raizes = []
        
        # Adicionar números baseados na frequência
        raizes.extend(numeros_frequentes[:n_raizes])
        
        # Adicionar números baseados no padrão de paridade
        pares_desejados, impares_desejados = padrao_comum
        
        # Adicionar um número baseado na soma média
        raiz_soma = soma_media % 60 + 1
        if raiz_soma not in raizes:
            raizes.append(raiz_soma)
        
        # Garantir que temos exatamente n_raizes
        while len(raizes) < n_raizes:
            novo_num = random.randint(1, 60)
            if novo_num not in raizes:
                raizes.append(novo_num)
        
        raizes = raizes[:n_raizes]  # Limitar ao número desejado de raízes
        
        return sorted(raizes)
    
    def _calcular_diferenca_raizes(self, raizes1, raizes2):
        """
        Calcula a diferença entre dois conjuntos de raízes.
        
        Args:
            raizes1: Primeiro conjunto de raízes.
            raizes2: Segundo conjunto de raízes.
        
        Returns:
            float: Valor entre 0 e 1 representando a diferença.
        """
        # Calcular quantos números são diferentes
        diferentes = sum(1 for r in raizes1 if r not in raizes2)
        return diferentes / len(raizes1)
    
    def simular_geracao_numeros(self, raizes, n_sorteios=10):
        """
        Simula a geração de números a partir de raízes usando um algoritmo pseudoaleatório.
        
        Args:
            raizes: Lista de números raízes.
            n_sorteios: Número de sorteios a gerar.
        
        Returns:
            List: Lista de sorteios gerados.
        """
        sorteios_gerados = []
        
        for _ in range(n_sorteios):
            # Usar as raízes como sementes para um gerador pseudoaleatório
            random.seed(sum(raizes))
            
            # Gerar um conjunto de 6 números
            numeros = []
            while len(numeros) < 6:
                # Usar as raízes para influenciar a geração
                for raiz in raizes:
                    num = (raiz * random.randint(1, 60)) % 60 + 1
                    if num not in numeros and 1 <= num <= 60:
                        numeros.append(num)
                        if len(numeros) >= 6:
                            break
            
            sorteios_gerados.append(sorted(numeros[:6]))
            
            # Modificar as raízes para o próximo sorteio
            raizes = [(r * 17 + 13) % 60 + 1 for r in raizes]
        
        return sorteios_gerados
    
    def implementar_simulacao_quantica(self, janela_sorteios):
        """
        Implementa uma simulação quântica para tentar identificar padrões ocultos.
        
        Args:
            janela_sorteios: Lista de sorteios para análise.
        
        Returns:
            List: Lista de possíveis números raízes.
        """
        # Preparar os dados para a simulação quântica
        dados_planificados = []
        for sorteio in janela_sorteios:
            # Normalizar os números para o intervalo [0, 1]
            normalizado = [n/60 for n in sorteio]
            dados_planificados.extend(normalizado)
        
        # Limitar o tamanho dos dados para a simulação
        dados_planificados = dados_planificados[:100]
        
        # Definir o dispositivo quântico
        n_qubits = 6
        dev = qml.device("default.qubit", wires=n_qubits, shots=1000)
        
        # Definir o circuito quântico
        @qml.qnode(dev)
        def circuito_quantico(params):
            # Preparar o estado inicial
            for i in range(n_qubits):
                qml.RY(params[i], wires=i)
            
            # Criar emaranhamento
            for i in range(n_qubits-1):
                qml.CNOT(wires=[i, i+1])
            
            # Aplicar rotações baseadas nos dados
            for i in range(n_qubits):
                idx = i % len(dados_planificados)
                qml.RZ(np.pi * dados_planificados[idx], wires=i)
            
            # Criar mais emaranhamento
            for i in range(n_qubits-1, 0, -1):
                qml.CNOT(wires=[i, i-1])
            
            # Medir as probabilidades
            return [qml.probs(wires=i) for i in range(n_qubits)]
        
        # Inicializar parâmetros aleatórios
        params_iniciais = np.random.uniform(0, np.pi, n_qubits)
        
        # Executar o circuito
        resultado = circuito_quantico(params_iniciais)
        
        # Converter resultados quânticos em possíveis números raízes
        raizes = []
        for prob in resultado:
            # Usar a probabilidade para determinar um número entre 1 e 60
            valor = int(np.argmax(prob) * 30 + 1)
            if 1 <= valor <= 60 and valor not in raizes:
                raizes.append(valor)
        
        # Garantir que temos pelo menos 3 raízes
        while len(raizes) < 3:
            novo_num = random.randint(1, 60)
            if novo_num not in raizes:
                raizes.append(novo_num)
        
        return sorted(raizes[:3])  # Retornar as 3 primeiras raízes
    
    def treinar_modelo_previsao(self, tamanho_teste=10):
        """
        Treina um modelo para prever sorteios futuros com base nos anteriores.
        
        Args:
            tamanho_teste: Número de sorteios a reservar para teste.
        
        Returns:
            float: Pontuação de acerto do modelo.
        """
        if len(self.sorteios) < tamanho_teste + 10:
            print("Dados insuficientes para treinar o modelo.")
            return 0
        
        # Dividir dados em treino e teste
        sorteios_treino = self.sorteios[:-tamanho_teste]
        sorteios_teste = self.sorteios[-tamanho_teste:]
        
        # Detectar números raízes nos dados de treino
        self.detectar_numeros_raizes(tamanho_janela=min(100, len(sorteios_treino)))
        
        # Usar as últimas raízes detectadas
        if not self.numeros_raizes:
            print("Não foi possível detectar números raízes.")
            return 0
        
        ultimas_raizes = self.numeros_raizes[-1][1]
        
        # Gerar previsões
        previsoes = self.simular_geracao_numeros(ultimas_raizes, n_sorteios=tamanho_teste)
        
        # Avaliar as previsões
        acertos_totais = 0
        for prev, real in zip(previsoes, sorteios_teste):
            acertos = len(set(prev).intersection(set(real)))
            acertos_totais += acertos
        
        pontuacao = acertos_totais / (tamanho_teste * 6)  # Normalizar para [0, 1]
        
        print(f"Modelo treinado. Pontuação de acerto: {pontuacao:.4f}")
        self.modelo_treinado = True
        
        return pontuacao
    
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
        
        # Usar sorteios de início até fim-1 para prever o sorteio fim
        sorteios_treino = self.sorteios[inicio:fim]
        sorteio_alvo = self.sorteios[fim]
        
        # Detectar raízes na sequência de treino
        raizes = self._encontrar_raizes_em_janela(sorteios_treino, n_raizes=3)
        
        # Gerar uma previsão
        previsao = self.simular_geracao_numeros(raizes, n_sorteios=1)[0]
        
        # Calcular acertos
        acertos = len(set(previsao).intersection(set(sorteio_alvo)))
        
        resultado = {
            "sorteio_previsto": fim,
            "numeros_reais": sorteio_alvo,
            "previsao": previsao,
            "acertos": acertos,
            "raizes_detectadas": raizes
        }
        
        print(f"Validação para sorteio {fim}:")
        print(f"Números reais: {sorteio_alvo}")
        print(f"Previsão: {previsao}")
        print(f"Acertos: {acertos}/6")
        
        return resultado
    
    def gerar_previsoes_finais(self, n_previsoes=5):
        """
        Gera previsões finais para jogos futuros.
        
        Args:
            n_previsoes: Número de previsões a gerar.
        
        Returns:
            List: Lista de previsões.
        """
        if not self.sorteios:
            print("Nenhum dado disponível para gerar previsões.")
            return []
        
        # Se o modelo não foi treinado, treinar agora
        if not self.modelo_treinado:
            self.treinar_modelo_previsao()
        
        # Detectar as raízes mais recentes se necessário
        if not self.numeros_raizes:
            self.detectar_numeros_raizes()
        
        # Usar as raízes mais recentes
        raizes_recentes = self.numeros_raizes[-1][1] if self.numeros_raizes else [10, 25, 53]
        
        # Gerar previsões usando simulação quântica
        previsoes_quanticas = []
        for _ in range(max(1, n_previsoes // 2)):
            # Usar os últimos 20 sorteios para a simulação quântica
            ultimos_sorteios = self.sorteios[-20:] if len(self.sorteios) >= 20 else self.sorteios
            raizes_quanticas = self.implementar_simulacao_quantica(ultimos_sorteios)
            previsao = self.simular_geracao_numeros(raizes_quanticas, n_sorteios=1)[0]
            if previsao not in previsoes_quanticas:
                previsoes_quanticas.append(previsao)
        
        # Gerar previsões usando o algoritmo de números raízes
        previsoes_raizes = self.simular_geracao_numeros(raizes_recentes, n_sorteios=n_previsoes)
        
        # Combinar as previsões, removendo duplicatas
        todas_previsoes = []
        for p in previsoes_quanticas + previsoes_raizes:
            if p not in todas_previsoes:
                todas_previsoes.append(p)
        
        # Limitar ao número solicitado
        previsoes_finais = todas_previsoes[:n_previsoes]
        
        print(f"Geradas {len(previsoes_finais)} previsões finais.")
        for i, prev in enumerate(previsoes_finais, 1):
            print(f"Previsão {i}: {prev}")
        
        return previsoes_finais
    
    def salvar_previsoes(self, previsoes, arquivo="previsoes_numeros_raizes.json"):
        """
        Salva as previsões em um arquivo JSON.
        
        Args:
            previsoes: Lista de previsões.
            arquivo: Nome do arquivo para salvar.
        
        Returns:
            bool: True se as previsões foram salvas com sucesso, False caso contrário.
        """
        try:
            data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
            dados_saida = {
                "da
(Content truncated due to size limit. Use line ranges to read in chunks)
import numpy as np
import pennylane as qml
import matplotlib.pyplot as plt
import json
import random
from collections import Counter

class SimulacaoQuanticaAvancada:
    """
    Classe para implementar simulações quânticas avançadas para análise de padrões
    ocultos nos dados da Mega Sena e geração de previsões.
    """
    
    def __init__(self, n_qubits=8):
        """
        Inicializa o simulador quântico avançado.
        
        Args:
            n_qubits: Número de qubits a utilizar na simulação.
        """
        self.n_qubits = n_qubits
        self.dev = qml.device("default.qubit", wires=n_qubits)
        self.dev_shots = qml.device("default.qubit", wires=n_qubits, shots=1000)
        self.resultados_analise = {}
    
    def preparar_dados_entrada(self, sorteios, metodo='normalizado'):
        """
        Prepara os dados de sorteios para entrada no circuito quântico.
        
        Args:
            sorteios: Lista de sorteios.
            metodo: Método de preparação ('normalizado', 'binario', 'fase').
        
        Returns:
            np.array: Array com dados preparados para entrada no circuito quântico.
        """
        if metodo == 'normalizado':
            # Normalizar números para o intervalo [0, 1]
            dados = []
            for sorteio in sorteios:
                normalizado = [n/60 for n in sorteio]
                dados.extend(normalizado)
            
        elif metodo == 'binario':
            # Converter para representação binária (presença/ausência)
            dados = np.zeros(60)
            for sorteio in sorteios:
                for num in sorteio:
                    dados[num-1] += 1
            # Normalizar
            if np.max(dados) > 0:
                dados = dados / np.max(dados)
            
        elif metodo == 'fase':
            # Usar números como ângulos de fase
            dados = []
            for sorteio in sorteios:
                fases = [n * np.pi / 30 for n in sorteio]  # Mapear para [0, 2π]
                dados.extend(fases)
        
        else:
            raise ValueError(f"Método de preparação desconhecido: {metodo}")
        
        # Limitar o tamanho para evitar sobrecarga
        return np.array(dados[:100])
    
    def circuito_grover_avancado(self, dados_entrada):
        """
        Implementa um circuito quântico avançado baseado no algoritmo de Grover
        para identificar padrões nos dados.
        
        Args:
            dados_entrada: Dados de entrada preparados.
        
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
            
            # Implementar iterações de Grover
            n_iteracoes = int(np.sqrt(2**self.n_qubits) / 4)
            for _ in range(n_iteracoes):
                # Oráculo (marca estados alvo)
                for i in range(self.n_qubits):
                    idx = i % len(dados_entrada)
                    if dados_entrada[idx] > 0.5:  # Condição para marcar estado
                        qml.PhaseShift(np.pi, wires=i)
                
                # Difusão (amplifica amplitude dos estados marcados)
                for i in range(self.n_qubits):
                    qml.Hadamard(wires=i)
                    qml.PhaseShift(np.pi, wires=i)
                
                # Operação de controle multi-qubit
                qml.ctrl(qml.PauliX, control=list(range(self.n_qubits-1)))(wires=self.n_qubits-1)
                
                # Desfazer fase e Hadamard
                for i in range(self.n_qubits):
                    qml.PhaseShift(np.pi, wires=i)
                    qml.Hadamard(wires=i)
            
            # Retornar probabilidades de todos os qubits
            return [qml.probs(wires=i) for i in range(self.n_qubits)]
        
        return circuito
    
    def circuito_qft_avancado(self, dados_entrada):
        """
        Implementa um circuito quântico avançado baseado na Transformada Quântica de Fourier
        para identificar periodicidades nos dados.
        
        Args:
            dados_entrada: Dados de entrada preparados.
        
        Returns:
            function: Função do circuito quântico.
        """
        @qml.qnode(self.dev)
        def circuito(params):
            # Preparar estado inicial baseado nos dados
            for i in range(self.n_qubits):
                idx = i % len(dados_entrada)
                qml.RY(np.pi * dados_entrada[idx], wires=i)
            
            # Aplicar transformações baseadas nos parâmetros
            for i in range(self.n_qubits):
                qml.RZ(params[i], wires=i)
            
            # Aplicar QFT
            qml.QFT(wires=range(self.n_qubits))
            
            # Aplicar operações de fase adicionais
            for i in range(self.n_qubits):
                idx = (i + self.n_qubits//2) % len(dados_entrada)
                qml.RZ(np.pi * dados_entrada[idx], wires=i)
            
            # Aplicar QFT inversa
            qml.adjoint(qml.QFT)(wires=range(self.n_qubits))
            
            # Retornar probabilidades de todos os qubits
            return [qml.probs(wires=i) for i in range(self.n_qubits)]
        
        return circuito
    
    def circuito_vqe_avancado(self, dados_entrada):
        """
        Implementa um circuito quântico avançado baseado em VQE (Variational Quantum Eigensolver)
        para encontrar padrões de energia mínima nos dados.
        
        Args:
            dados_entrada: Dados de entrada preparados.
        
        Returns:
            function: Função do circuito quântico.
        """
        @qml.qnode(self.dev)
        def circuito(params):
            # Preparar estado inicial
            for i in range(self.n_qubits):
                qml.RY(params[i], wires=i)
            
            # Criar camadas de emaranhamento e rotação
            n_camadas = 3
            param_idx = self.n_qubits
            
            for l in range(n_camadas):
                # Camada de emaranhamento
                for i in range(self.n_qubits - 1):
                    qml.CNOT(wires=[i, i+1])
                
                # Camada de rotações
                for i in range(self.n_qubits):
                    idx = (i + l) % len(dados_entrada)
                    # Rotações baseadas nos dados e parâmetros
                    qml.RX(params[param_idx] * dados_entrada[idx], wires=i)
                    param_idx += 1
                    qml.RY(params[param_idx], wires=i)
                    param_idx += 1
                    qml.RZ(params[param_idx], wires=i)
                    param_idx += 1
            
            # Retornar probabilidades de todos os qubits
            return [qml.probs(wires=i) for i in range(self.n_qubits)]
        
        return circuito
    
    def circuito_qwalk_avancado(self, dados_entrada):
        """
        Implementa um circuito quântico avançado baseado em caminhada quântica
        para explorar o espaço de soluções.
        
        Args:
            dados_entrada: Dados de entrada preparados.
        
        Returns:
            function: Função do circuito quântico.
        """
        @qml.qnode(self.dev_shots)
        def circuito(params):
            # Preparar estado inicial
            for i in range(self.n_qubits):
                qml.RY(params[i], wires=i)
            
            # Implementar caminhada quântica
            n_passos = 5
            
            # Inicializar a "moeda" quântica
            for i in range(self.n_qubits):
                qml.Hadamard(wires=i)
            
            for step in range(n_passos):
                # Operação de deslocamento condicional
                for i in range(self.n_qubits - 1):
                    qml.CNOT(wires=[i, (i+1) % self.n_qubits])
                
                # Aplicar rotações baseadas nos dados
                for i in range(self.n_qubits):
                    idx = (i + step) % len(dados_entrada)
                    qml.RZ(np.pi * dados_entrada[idx], wires=i)
                
                # Atualizar a "moeda" quântica
                for i in range(self.n_qubits):
                    qml.RY(params[i + step % len(params)], wires=i)
                    qml.Hadamard(wires=i)
            
            # Medir no final da caminhada
            return [qml.sample(wires=i) for i in range(self.n_qubits)]
        
        return circuito
    
    def circuito_hibrido_avancado(self, dados_entrada, raizes):
        """
        Implementa um circuito quântico híbrido que combina informações dos números raízes
        com simulação quântica.
        
        Args:
            dados_entrada: Dados de entrada preparados.
            raizes: Lista de números raízes detectados.
        
        Returns:
            function: Função do circuito quântico.
        """
        # Converter raízes para valores normalizados
        raizes_norm = [r/60 for r in raizes]
        
        @qml.qnode(self.dev)
        def circuito(params):
            # Preparar estado inicial baseado nas raízes
            for i in range(min(len(raizes_norm), self.n_qubits)):
                qml.RY(np.pi * raizes_norm[i], wires=i)
            
            # Completar inicialização para qubits restantes
            for i in range(len(raizes_norm), self.n_qubits):
                qml.RY(params[i], wires=i)
            
            # Criar emaranhamento
            for i in range(self.n_qubits - 1):
                qml.CNOT(wires=[i, i+1])
            
            # Aplicar operações baseadas nos dados históricos
            for i in range(self.n_qubits):
                idx = i % len(dados_entrada)
                qml.RZ(np.pi * dados_entrada[idx], wires=i)
            
            # Aplicar transformações paramétricas
            for i in range(self.n_qubits):
                qml.RX(params[i], wires=i)
                qml.RZ(params[i + self.n_qubits], wires=i)
            
            # Criar mais emaranhamento
            for i in range(self.n_qubits - 1, 0, -1):
                qml.CNOT(wires=[i, i-1])
            
            # Retornar probabilidades de todos os qubits
            return [qml.probs(wires=i) for i in range(self.n_qubits)]
        
        return circuito
    
    def converter_para_numeros_mega(self, resultados_quanticos, metodo='probabilidade'):
        """
        Converte resultados quânticos em números para a Mega Sena.
        
        Args:
            resultados_quanticos: Lista de arrays de probabilidades ou amostras.
            metodo: Método de conversão ('probabilidade', 'amostragem', 'combinado').
        
        Returns:
            list: Lista de 6 números entre 1 e 60.
        """
        numeros = []
        
        if metodo == 'probabilidade':
            # Usar probabilidades para gerar números
            for probs in resultados_quanticos:
                if isinstance(probs, np.ndarray) and len(probs.shape) > 0:
                    # Encontrar índice de maior probabilidade
                    idx_max = np.argmax(probs)
                    
                    # Mapear para o intervalo [1, 60]
                    num = int(idx_max * (60 / (2**len(probs.shape))) + 1)
                    num = max(1, min(60, num))
                    
                    if num not in numeros:
                        numeros.append(num)
        
        elif metodo == 'amostragem':
            # Usar amostras para gerar números
            for amostras in resultados_quanticos:
                if isinstance(amostras, np.ndarray) and len(amostras) > 0:
                    # Contar frequência das amostras
                    contador = Counter(amostras)
                    valor_mais_comum = contador.most_common(1)[0][0]
                    
                    # Mapear para o intervalo [1, 60]
                    num = int(valor_mais_comum * 30 + 1)
                    num = max(1, min(60, num))
                    
                    if num not in numeros:
                        numeros.append(num)
        
        elif metodo == 'combinado':
            # Combinar probabilidades e valores de qubits
            valores_qubits = []
            
            for probs in resultados_quanticos:
                if isinstance(probs, np.ndarray) and len(probs.shape) > 0:
                    # Calcular valor esperado
                    val = 0
                    for i, p in enumerate(probs):
                        val += i * p
                    valores_qubits.append(val)
            
            # Usar combinações dos valores para gerar números
            for i in range(len(valores_qubits)):
                for j in range(i+1, len(valores_qubits)):
                    # Combinar valores de dois qubits
                    val = (valores_qubits[i] + valores_qubits[j]) % 60 + 1
                    if val not in numeros:
                        numeros.append(int(val))
        
        # Garantir que temos 6 números únicos
        while len(numeros) < 6:
            num = random.randint(1, 60)
            if num not in numeros:
                numeros.append(num)
        
        # Limitar a 6 números
        return sorted(numeros[:6])
    
    def analisar_dados_quanticos(self, sorteios, raizes=None):
        """
        Realiza uma análise quântica completa dos dados históricos.
        
        Args:
            sorteios: Lista de sorteios históricos.
            raizes: Lista opcional de números raízes detectados.
        
        Returns:
            dict: Resultados da análise quântica.
        """
        print("Iniciando análise quântica avançada dos dados...")
        
        # Usar os últimos 20 sorteios para análise mais recente
        sorteios_recentes = sorteios[-20:] if len(sorteios) > 20 else sorteios
        
        # Preparar dados de entrada com diferentes métodos
        dados_norm = self.preparar_dados_entrada(sorteios_recentes, 'normalizado')
        dados_bin = self.preparar_dados_entrada(sorteios_recentes, 'binario')
        dados_fase = self.preparar_dados_entrada(sorteios_recentes, 'fase')
        
        # Inicializar parâmetros
        params_grover = np.random.uniform(0, np.pi, self.n_qubits)
        params_qft = np.random.uniform(0, np.pi, self.n_qubits)
        params_vqe = np.random.uniform(0, np.pi, self.n_qubits * (1 + 3 * 3))  # Parâmetros para VQE
        params_qwalk = np.random.uniform(0, np.pi, self.n_qubits + 5)  # Parâmetros para caminhada quântica
        params_hibrido = np.random.uniform(0, np.pi, self.n_qubits * 2)  # Parâmetros para circuito híbrido
        
        # Executar circuitos quânticos
        resultados = {}
        
        print("Executando circuito Grover avançado...")
        circuito_grover = self.circuito_grover_avancado(dados_norm)
        resultados['grover'] = circuito_grover(params_grover)
        
        print("Executando circuito QFT avançado...")
        circuito_qft = self.circuito_qft_avancado(dados_fase)
        resultados['qft'] = circuito_qft(params_qft)
        
        print("Executando circuito VQE avançado...")
        circuito_vqe = self.circuito_vqe_avancado(dados_bin)
        resultados['vqe'] = circuito_vqe(params_vqe)
        
        print("Executando circuito de caminhada quântica avançada...")
        circuito_qwalk = self.circuito_qwalk_avancado(dados_norm)
        resultados['qwalk'] = circuito_qwalk(params_qwalk)
        
        # Se temos números raízes, executar o circuito híbrido
        if raizes:
            print("Executando circuito híbrido avançado...")
            circuito_hibrido = self.circuito_hibrido_avancado(dados_norm, raizes)
            resultados['hibrido'] = circuito_hibrido(params_hibrido)
        
        # Converter resultados quânticos em números da Mega Sena
        previsoes = {}
        
        previsoes['grover'] = self.converter_para_numeros_mega(resultados['grover'], 'probabilidade')
        previsoes['qft'] = self.converter_para_numeros_mega(resultados['qft'], 'probabilidade')
        previsoes['vqe'] = self.converter_para_numeros_mega(resultados['vqe'], 'probabilidade')
        previsoes['qwalk'] = self.converter_para_numeros_mega(resultados['qwalk'], 'amostragem')
        
        if raizes:
            previsoes['hibrido'] = self.converter_para_numeros_mega(resultados['hibrido'], 'combinado')
        
        # Analisar padrões quânticos
        padroes_quanticos = self.analisar_padroes_quanticos(resultados)
        
        # Armazenar resultados
        self.resultados_analise = {
            'previsoes': previsoes,
            'padroes_quanticos': padroes_quanticos
        }
        
        print("Análise quântica concluída.")
        print("\nPrevisões geradas pelos circuitos quânticos:")
        for metodo, numeros in previsoes.items():
            print(f"{metodo}: {numeros}")
        
        return self.resultados_analise
    
    def analisar_padroes_quanticos(self, resultados_quanticos):
        """
        Analisa os resultados quânticos para identificar padrões.
        
        Args:
            resultados_quanticos: Dicionário com resultados dos circuitos quânticos.
        
        Returns:
            dict: Padrões identificados.
        """
        padroes = {}
        
        # Analisar distribuição de probabilidades
        for metodo, resultado in resultados_quanticos.items():
            if metodo != 'qwalk':  # Qwalk retorna amostras, não probabilidades
                # Calcular entropia das distribuições de probabilidade
                entropia = 0
                for probs in resultado:
                    if isinstance(probs, np.ndarray) and len(probs.shape) > 0:
                        # Evitar log(0)
                        probs_clean = np.clip(probs, 1e-10, 1.0)
                        entropia -= np.sum(probs_clean * np.log2(probs_clean))
                
                padroes[f'entropia_{metodo}'] = entropia / len(resultado)
                
                # Identificar qubits com distribuição mais polarizada
                polarizacao = []
                for i, probs in enumerate(resultado):
                    if isinstance(probs, np.ndarray) and len(probs.shape) > 0:
                        # Calcular quão polarizada é a distribuição
                        pol = np.max(probs) - np.min(probs)
                        polarizacao.append((i, pol))
                
                # Ordenar por polarização
                polarizacao_ordenada = sorted(polarizacao, key=lambda x: x[1], reverse=True)
                padroes[f'qubits_polarizados_{metodo}'] = [q for q, _ in polarizacao_ordenada[:3]]
        
        # Analisar correlações entre qubits (para métodos que não são qwalk)
        for metodo, resultado in resultados_quanticos.items():
            if metodo != 'qwalk' and len(resultado) >= 2:
                correlacoes = []
                for i in range(len(resultado)):
                    for j in range(i+1, len(resultado)):
                        if isinstance(resultado[i], np.ndarray) and isinstance(resultado[j], np.ndarray):
                            # Calcular uma medida simples de correlação
                            corr = np.abs(np.mean(resultado[i]) - np.mean(resultado[j]))
                            correlacoes.append(((i, j), corr))
                
                # Ordenar por correlação
                correlacoes_ordenadas = sorted(correlacoes, key=lambda x: x[1])
                padroes[f'qubits_correlacionados_{metodo}'] = [q for q, _ in correlacoes_ordenadas[:3]]
        
        return padroes
    
    def gerar_previsoes_quanticas(self, sorteios, raizes=None, n_previsoes=5):
        """
        Gera previsões para jogos futuros usando simulação quântica avançada.
        
        Args:
            sorteios: Lista de sorteios históricos.
            raizes: Lista opcional de números raízes detectados.
            n_previsoes: Número de previsões a gerar.
        
        Returns:
            list: Lista de previsões.
        """
        # Se ainda não temos resultados de análise, realizar análise
        if not self.resultados_analise:
            self.analisar_dados_quanticos(sorteios, raizes)
        
        previsoes = []
        metodos = list(self.resultados_analise['previsoes'].keys())
        
        # Adicionar previsões diretas dos circuitos quânticos
        for metodo in metodos:
            previsao = self.resultados_analise['previsoes'][metodo]
            previsoes.append({
                'metodo': f'quantico_{metodo}',
                'numeros': previsao,
                'descricao': f'Gerada pelo circuito quântico {metodo}'
            })
        
        # Se temos raízes, gerar previsões combinadas
        if raizes and len(previsoes) < n_previsoes:
            # Combinar raízes com resultados quânticos
            for metodo in metodos[:2]:  # Usar apenas os dois primeiros métodos
                numeros_combinados = []
                
                # Incluir algumas raízes
                for raiz in raizes[:2]:
                    if raiz not in numeros_combinados:
                        numeros_combinados.append(raiz)
                
                # Incluir alguns números da previsão quântica
                previsao_quantica = self.resultados_analise['previsoes'][metodo]
                for num in previsao_quantica:
                    if num not in numeros_combinados and len(numeros_combinados) < 4:
                        numeros_combinados.append(num)
                
                # Completar com números derivados
                while len(numeros_combinados) < 6:
                    # Gerar número baseado nas raízes e números já selecionados
                    soma = sum(numeros_combinados) + sum(raizes)
                    novo_num = soma % 60 + 1
                    
                    if novo_num not in numeros_combinados:
                        numeros_combinados.append(novo_num)
                    else:
                        # Tentar outra abordagem
                        produto = 1
                        for n in numeros_combinados[:2]:
                            produto *= n
                        novo_num = produto % 60 + 1
                        
                        if novo_num not in numeros_combinados:
                            numeros_combinados.append(novo_num)
                        else:
                            # Último recurso: número aleatório
                            while len(numeros_combinados) < 6:
                                num = random.randint(1, 60)
                                if num not in numeros_combinados:
                                    numeros_combinados.append(num)
                
                previsoes.append({
                    'metodo': f'combinado_raizes_{metodo}',
                    'numeros': sorted(numeros_combinados),
                    'descricao': f'Combinação de números raízes com circuito {metodo}'
                })
        
        # Gerar previsão baseada em padrões quânticos identificados
        if len(previsoes) < n_previsoes:
            # Usar informações de qubits polarizados
            numeros_padroes = []
            
            # Coletar qubits polarizados de diferentes métodos
            qubits_importantes = []
            for metodo in metodos:
                chave = f'qubits_polarizados_{metodo}'
                if chave in self.resultados_analise['padroes_quanticos']:
                    qubits_importantes.extend(self.resultados_analise['padroes_quanticos'][chave])
            
            # Usar os qubits importantes para gerar números
            for q in qubits_importantes:
                num = (q * 7 + 1) % 60 + 1
                if num not in numeros_padroes:
                    numeros_padroes.append(num)
            
            # Completar com números baseados em entropia
            entropias = []
            for metodo in metodos:
                chave = f'entropia_{metodo}'
                if chave in self.resultados_analise['padroes_quanticos']:
                    entropias.append(self.resultados_analise['padroes_quanticos'][chave])
            
            if entropias:
                entropia_media = sum(entropias) / len(entropias)
                num = int(entropia_media * 10) % 60 + 1
                if num not in numeros_padroes:
                    numeros_padroes.append(num)
            
            # Completar com números aleatórios
            while len(numeros_padroes) < 6:
                num = random.randint(1, 60)
                if num not in numeros_padroes:
                    numeros_padroes.append(num)
            
            previsoes.append({
                'metodo': 'padroes_quanticos',
                'numeros': sorted(numeros_padroes),
                'descricao': 'Baseada em padrões quânticos identificados na análise'
            })
        
        # Limitar ao número solicitado
        return previsoes[:n_previsoes]
    
    def visualizar_estados_quanticos(self, arquivo_saida="estados_quanticos.png"):
        """
        Cria uma visualização dos estados quânticos gerados pelos diferentes circuitos.
        
        Args:
            arquivo_saida: Nome do arquivo para salvar a visualização.
        
        Returns:
            str: Caminho para o arquivo de visualização.
        """
        if not self.resultados_analise:
            print("Execute analisar_dados_quanticos() primeiro.")
            return None
        
        plt.figure(figsize=(15, 10))
        
        # Configurar subplots
        n_metodos = len(self.resultados_analise['previsoes'])
        n_rows = (n_metodos + 1) // 2
        n_cols = min(n_metodos, 2)
        
        # Plotar distribuições de probabilidade para cada método
        for i, (metodo, previsao) in enumerate(self.resultados_analise['previsoes'].items()):
            plt.subplot(n_rows, n_cols, i+1)
            
            # Plotar os números previstos
            plt.bar(range(1, 61), [1 if j in previsao else 0 for j in range(1, 61)])
            plt.title(f'Previsão do circuito {metodo}')
            plt.xlabel('Número')
            plt.ylabel('Selecionado')
            plt.xticks(range(0, 61, 10))
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(arquivo_saida)
        plt.close()
        
        print(f"Visualização salva em {arquivo_saida}")
        return arquivo_saida


def testar_simulacao_quantica():
    """
    Função para testar a simulação quântica avançada.
    """
    print("\n===== Teste de Simulação Quântica Avançada =====")
    
    # Criar alguns dados de teste
    sorteios_teste = [
        [1, 15, 23, 35, 47, 59],
        [5, 10, 22, 30, 45, 55],
        [7, 12, 25, 33, 40, 52],
        [3, 18, 27, 38, 42, 50],
        [9, 14, 21, 36, 44, 58]
    ]
    
    raizes_teste = [10, 25, 42]
    
    # Criar simulador
    simulador = SimulacaoQuanticaAvancada(n_qubits=6)
    
    # Testar análise quântica
    resultados = simulador.analisar_dados_quanticos(sorteios_teste, raizes_teste)
    
    # Testar geração de previsões
    previsoes = simulador.gerar_previsoes_quanticas(sorteios_teste, raizes_teste, n_previsoes=3)
    
    print("\nPrevisões geradas:")
    for i, prev in enumerate(previsoes, 1):
        print(f"{i}. Método: {prev['metodo']} - Números: {prev['numeros']}")
        print(f"   {prev['descricao']}")
    
    # Testar visualização
    simulador.visualizar_estados_quanticos("teste_estados_quanticos.png")
    
    print("\n===== Teste concluído =====")


if __name__ == "__main__":
    testar_simulacao_quantica()

import numpy as np
import matplotlib.pyplot as plt
import json
import os
from collections import Counter
from scipy.signal import find_peaks
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import datetime
import pandas as pd

class DetectorMudancasTemporais:
    """
    Classe para detectar mudanças temporais nos números raízes que poderiam estar
    gerando os resultados da Mega Sena.
    """
    
    def __init__(self):
        """Inicializa o detector de mudanças temporais."""
        self.dados_historicos = {}
        self.sorteios = []
        self.series_temporais = {}
        self.pontos_mudanca = []
        self.periodos_estabilidade = []
        self.metricas_temporais = {}
    
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
    
    def gerar_series_temporais(self):
        """
        Gera séries temporais a partir dos dados históricos para análise de mudanças.
        
        Returns:
            dict: Dicionário com diferentes séries temporais.
        """
        if not self.sorteios:
            print("Nenhum dado carregado para análise.")
            return {}
        
        # Série 1: Média dos números por sorteio
        medias = [np.mean(sorteio) for sorteio in self.sorteios]
        
        # Série 2: Desvio padrão dos números por sorteio
        desvios = [np.std(sorteio) for sorteio in self.sorteios]
        
        # Série 3: Soma dos números por sorteio
        somas = [sum(sorteio) for sorteio in self.sorteios]
        
        # Série 4: Número de pares por sorteio
        n_pares = [sum(1 for n in sorteio if n % 2 == 0) for sorteio in self.sorteios]
        
        # Série 5: Amplitude (máximo - mínimo) por sorteio
        amplitudes = [max(sorteio) - min(sorteio) for sorteio in self.sorteios]
        
        # Série 6: Distância média entre números consecutivos
        distancias = []
        for sorteio in self.sorteios:
            sorteio_ordenado = sorted(sorteio)
            dist = np.mean([sorteio_ordenado[i+1] - sorteio_ordenado[i] for i in range(len(sorteio_ordenado)-1)])
            distancias.append(dist)
        
        # Série 7: Frequência acumulada dos números
        freq_acumulada = []
        contador = Counter()
        for sorteio in self.sorteios:
            for num in sorteio:
                contador[num] += 1
            # Calcular entropia da distribuição atual
            total = sum(contador.values())
            if total > 0:
                probs = [count/total for count in contador.values()]
                entropia = -sum(p * np.log2(p) if p > 0 else 0 for p in probs)
                freq_acumulada.append(entropia)
            else:
                freq_acumulada.append(0)
        
        # Armazenar todas as séries
        self.series_temporais = {
            'media': medias,
            'desvio': desvios,
            'soma': somas,
            'n_pares': n_pares,
            'amplitude': amplitudes,
            'distancia': distancias,
            'entropia': freq_acumulada
        }
        
        print(f"Geradas {len(self.series_temporais)} séries temporais para análise.")
        return self.series_temporais
    
    def detectar_pontos_mudanca(self, metodo='combinado', sensibilidade=1.5):
        """
        Detecta pontos onde ocorrem mudanças significativas nas séries temporais.
        
        Args:
            metodo: Método de detecção ('picos', 'kmeans', 'combinado').
            sensibilidade: Fator de sensibilidade para detecção (maior = mais sensível).
        
        Returns:
            list: Lista de pontos de mudança detectados.
        """
        if not self.series_temporais:
            print("Execute gerar_series_temporais() primeiro.")
            return []
        
        self.pontos_mudanca = []
        
        if metodo == 'picos' or metodo == 'combinado':
            # Detectar mudanças usando análise de picos nas derivadas das séries
            for nome, serie in self.series_temporais.items():
                # Calcular a derivada (diferença entre pontos consecutivos)
                derivada = np.diff(serie)
                
                # Normalizar a derivada
                if np.std(derivada) > 0:
                    derivada_norm = (derivada - np.mean(derivada)) / np.std(derivada)
                    
                    # Encontrar picos significativos (positivos e negativos)
                    limiar = sensibilidade
                    picos_pos, _ = find_peaks(derivada_norm, height=limiar)
                    picos_neg, _ = find_peaks(-derivada_norm, height=limiar)
                    
                    # Combinar picos
                    todos_picos = np.sort(np.concatenate([picos_pos, picos_neg]))
                    
                    # Adicionar pontos de mudança
                    for pico in todos_picos:
                        # Ajustar índice (a derivada tem um elemento a menos)
                        idx_ajustado = pico + 1
                        
                        # Verificar se já existe um ponto próximo
                        if not any(abs(p['indice'] - idx_ajustado) < 5 for p in self.pontos_mudanca):
                            self.pontos_mudanca.append({
                                'indice': idx_ajustado,
                                'serie': nome,
                                'valor_antes': serie[idx_ajustado-1] if idx_ajustado > 0 else None,
                                'valor_depois': serie[idx_ajustado] if idx_ajustado < len(serie) else None,
                                'metodo': 'picos'
                            })
        
        if metodo == 'kmeans' or metodo == 'combinado':
            # Detectar mudanças usando clustering das características
            # Preparar dados para clustering
            dados_cluster = []
            for i in range(len(self.sorteios)):
                if i < 10:  # Precisamos de alguns sorteios anteriores
                    continue
                
                # Extrair características da janela atual
                caracteristicas = []
                for nome, serie in self.series_temporais.items():
                    if i < len(serie):
                        caracteristicas.append(serie[i])
                
                dados_cluster.append(caracteristicas)
            
            if dados_cluster:
                # Normalizar dados
                dados_array = np.array(dados_cluster)
                dados_norm = (dados_array - np.mean(dados_array, axis=0)) / np.std(dados_array, axis=0)
                
                # Aplicar PCA para redução de dimensionalidade
                pca = PCA(n_components=min(3, dados_norm.shape[1]))
                dados_pca = pca.fit_transform(dados_norm)
                
                # Aplicar K-means
                n_clusters = min(5, len(dados_pca) // 10)  # Número razoável de clusters
                if n_clusters >= 2:
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                    clusters = kmeans.fit_predict(dados_pca)
                    
                    # Detectar mudanças de cluster
                    for i in range(1, len(clusters)):
                        if clusters[i] != clusters[i-1]:
                            # Ajustar índice (offset de 10 do início)
                            idx_ajustado = i + 10
                            
                            # Verificar se já existe um ponto próximo
                            if not any(abs(p['indice'] - idx_ajustado) < 5 for p in self.pontos_mudanca):
                                self.pontos_mudanca.append({
                                    'indice': idx_ajustado,
                                    'cluster_antes': int(clusters[i-1]),
                                    'cluster_depois': int(clusters[i]),
                                    'metodo': 'kmeans'
                                })
        
        # Ordenar pontos de mudança por índice
        self.pontos_mudanca.sort(key=lambda x: x['indice'])
        
        print(f"Detectados {len(self.pontos_mudanca)} pontos de mudança.")
        return self.pontos_mudanca
    
    def identificar_periodos_estabilidade(self, min_tamanho=20):
        """
        Identifica períodos de estabilidade entre pontos de mudança.
        
        Args:
            min_tamanho: Tamanho mínimo de um período para ser considerado estável.
        
        Returns:
            list: Lista de períodos de estabilidade.
        """
        if not self.pontos_mudanca:
            print("Execute detectar_pontos_mudanca() primeiro.")
            return []
        
        # Adicionar início e fim dos dados como pontos de referência
        pontos_ref = [0] + [p['indice'] for p in self.pontos_mudanca] + [len(self.sorteios)]
        
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
                raizes = self._extrair_raizes_periodo(sorteios_periodo)
                
                self.periodos_estabilidade.append({
                    'inicio': inicio,
                    'fim': fim,
                    'tamanho': fim - inicio,
                    'media_soma': media_soma,
                    'media_pares': media_pares,
                    'raizes': raizes
                })
        
        print(f"Identificados {len(self.periodos_estabilidade)} períodos de estabilidade.")
        return self.periodos_estabilidade
    
    def _extrair_raizes_periodo(self, sorteios, n_raizes=3):
        """
        Extrai possíveis números raízes de um período de sorteios.
        
        Args:
            sorteios: Lista de sorteios no período.
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
    
    def calcular_metricas_temporais(self):
        """
        Calcula métricas temporais para análise de padrões cíclicos.
        
        Returns:
            dict: Dicionário com métricas temporais.
        """
        if not self.sorteios:
            print("Nenhum dado carregado para análise.")
            return {}
        
        # Métrica 1: Autocorrelação das séries temporais
        autocorrelacoes = {}
        for nome, serie in self.series_temporais.items():
            # Calcular autocorrelação para diferentes lags
            ac = []
            for lag in range(1, min(50, len(serie) // 2)):
                # Calcular correlação entre a série e ela mesma com deslocamento
                serie_orig = serie[:-lag]
                serie_lag = serie[lag:]
                
                # Normalizar séries
                if np.std(serie_orig) > 0 and np.std(serie_lag) > 0:
                    serie_orig_norm = (serie_orig - np.mean(serie_orig)) / np.std(serie_orig)
                    serie_lag_norm = (serie_lag - np.mean(serie_lag)) / np.std(serie_lag)
                    
                    # Calcular correlação
                    corr = np.mean(serie_orig_norm * serie_lag_norm)
                    ac.append((lag, corr))
            
            autocorrelacoes[nome] = ac
        
        # Métrica 2: Análise de periodicidade
        periodicidades = {}
        for nome, ac in autocorrelacoes.items():
            if ac:
                # Encontrar picos na autocorrelação
                lags = [lag for lag, _ in ac]
                valores = [val for _, val in ac]
                
                # Normalizar valores
                if np.std(valores) > 0:
                    valores_norm = (valores - np.mean(valores)) / np.std(valores)
                    
                    # Encontrar picos
                    picos, _ = find_peaks(valores_norm, height=0.2)
                    
                    if len(picos) > 0:
                        # Converter índices de picos para lags
                        picos_lags = [lags[p] for p in picos if p < len(lags)]
                        periodicidades[nome] = picos_lags
        
        # Métrica 3: Análise de tendências
        tendencias = {}
        for nome, serie in self.series_temporais.items():
            # Dividir a série em segmentos
            n_segmentos = min(5, len(serie) // 50)
            if n_segmentos >= 2:
                tamanho_segmento = len(serie) // n_segmentos
                medias_segmentos = []
                
                for i in range(n_segmentos):
                    inicio = i * tamanho_segmento
                    fim = (i + 1) * tamanho_segmento if i < n_segmentos - 1 else len(serie)
                    segmento = serie[inicio:fim]
                    medias_segmentos.append(np.mean(segmento))
                
                # Calcular tendência (inclinação da reta)
                x = np.arange(n_segmentos)
                tendencia = np.polyfit(x, medias_segmentos, 1)[0]
                tendencias[nome] = tendencia
        
        # Armazenar métricas
        self.metricas_temporais = {
            'autocorrelacoes': autocorrelacoes,
            'periodicidades': periodicidades,
            'tendencias': tendencias
        }
        
        print("Métricas temporais calculadas com sucesso.")
        return self.metricas_temporais
    
    def prever_proxima_mudanca(self):
        """
        Prevê quando poderá ocorrer a próxima mudança nos números raízes.
        
        Returns:
            dict: Informações sobre a previsão da próxima mudança.
        """
        if not self.pontos_mudanca or not self.periodos_estabilidade:
            print("Execute detectar_pontos_mudanca() e identificar_periodos_estabilidade() primeiro.")
            return {}
        
        # Calcular intervalos entre mudanças anteriores
        intervalos = []
        for i in range(1, len(self.pontos_mudanca)):
            intervalo = self.pontos_mudanca[i]['indice'] - self.pontos_mudanca[i-1]['indice']
            intervalos.append(intervalo)
        
        if not intervalos:
            print("Dados insuficientes para prever próxima mudança.")
            return {}
        
        # Calcular estatísticas dos intervalos
        intervalo_medio = np.mean(intervalos)
        intervalo_mediano = np.median(intervalos)
        
        # Verificar se há periodicidade nas mudanças
        if not self.metricas_temporais:
            self.calcular_metricas_temporais()
        
        periodicidade_detectada = None
        for nome, periodos in self.metricas_temporais.get('periodicidades', {}).items():
            if periodos:
                # Usar o primeiro período detectado
                periodicidade_detectada = periodos[0]
                break
        
        # Determinar quando ocorreu a última mudança
        ultima_mudanca = self.pontos_mudanca[-1]['indice'] if self.pontos_mudanca else 0
        
        # Calcular previsão para próxima mudança
        if periodicidade_detectada:
            # Usar periodicidade detectada
            proxima_mudanca = ultima_mudanca + periodicidade_detectada
            metodo = 'periodicidade'
        else:
            # Usar média dos intervalos anteriores
            proxima_mudanca = ultima_mudanca + int(intervalo_medio)
            metodo = 'média_intervalos'
        
        # Verificar se a previsão está no futuro
        if proxima_mudanca <= len(self.sorteios):
            # Já deveria ter ocorrido, usar mediana para nova previsão
            proxima_mudanca = ultima_mudanca + int(intervalo_mediano)
            metodo = 'mediana_intervalos'
        
        # Calcular quantos sorteios faltam
        sorteios_restantes = proxima_mudanca - len(self.sorteios)
        
        resultado = {
            'ultima_mudanca': ultima_mudanca,
            'proxima_mudanca_prevista': proxima_mudanca,
            'sorteios_restantes': max(0, sorteios_restantes),
            'intervalo_medio_historico': intervalo_medio,
            'metodo_previsao': metodo
        }
        
        print(f"Previsão da próxima mudança: após {resultado['sorteios_restantes']} sorteios.")
        return resultado
    
    def visualizar_series_e_mudancas(self, arquivo_saida="series_e_mudancas.png"):
        """
        Cria uma visualização das séries temporais e pontos de mudança detectados.
        
        Args:
            arquivo_saida: Nome do arquivo para salvar a visualização.
        
        Returns:
            str: Caminho para o arquivo de visualização.
        """
        if not self.series_temporais:
            print("Execute gerar_series_temporais() primeiro.")
            return None
        
        plt.figure(figsize=(15, 10))
        
        # Selecionar séries mais informativas
        series_para_plotar = ['media', 'soma', 'n_pares', 'entropia']
        n_series = len(series_para_plotar)
        
        for i, nome in enumerate(series_para_plotar):
            plt.subplot(n_series, 1, i+1)
            
            # Plotar série temporal
            plt.plot(self.series_temporais[nome], label=nome)
            
            # Marcar pontos de mudança
            for ponto in self.pontos_mudanca:
                plt.axvline(x=ponto['indice'], color='r', linestyle='--', alpha=0.5)
            
            # Marcar períodos de estabilidade
            for periodo in self.periodos_estabilidade:
                plt.axvspan(periodo['inicio'], periodo['fim'], alpha=0.2, color='g')
            
            plt.title(f'Série Temporal: {nome}')
            plt.grid(True, alpha=0.3)
            plt.legend()
        
        plt.tight_layout()
        plt.savefig(arquivo_saida)
        plt.close()
        
        print(f"Visualização salva em {arquivo_saida}")
        return arquivo_saida
    
    def visualizar_raizes_por_periodo(self, arquivo_saida="raizes_por_periodo.png"):
        """
        Cria uma visualização dos números raízes detectados em cada período de estabilidade.
        
        Args:
            arquivo_saida: Nome do arquivo para salvar a visualização.
        
        Returns:
            str: Caminho para o arquivo de visualização.
        """
        if not self.periodos_estabilidade:
            print("Execute identificar_periodos_estabilidade() primeiro.")
            return None
        
        plt.figure(figsize=(12, 8))
        
        # Preparar dados para visualização
        periodos = range(len(self.periodos_estabilidade))
        
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
        
        # Adicionar informações sobre tamanho dos períodos
        for i, periodo in enumerate(self.periodos_estabilidade):
            plt.text(i, 5, f"n={periodo['tamanho']}", ha='center')
        
        plt.title('Evolução dos Números Raízes por Período de Estabilidade')
        plt.xlabel('Período')
        plt.ylabel('Valor da Raiz')
        plt.yticks(range(0, 61, 5))
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(arquivo_saida)
        plt.close()
        
        print(f"Visualização salva em {arquivo_saida}")
        return arquivo_saida


class AnalisadorMudancasTemporais:
    """
    Classe para analisar mudanças temporais nos padrões da Mega Sena e
    gerar previsões baseadas nessa análise.
    """
    
    def __init__(self):
        """Inicializa o analisador de mudanças temporais."""
        self.detector = DetectorMudancasTemporais()
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
    
    def analisar_mudancas_temporais(self, sensibilidade=1.5, min_tamanho_periodo=20):
        """
        Realiza a análise completa de mudanças temporais nos dados.
        
        Args:
            sensibilidade: Fator de sensibilidade para detecção de mudanças.
            min_tamanho_periodo: Tamanho mínimo de um período para ser considerado estável.
        
        Returns:
            dict: Resultados da análise.
        """
        # Gerar séries temporais
        self.detector.gerar_series_temporais()
        
        # Detectar pontos de mudança
        self.detector.detectar_pontos_mudanca(sensibilidade=sensibilidade)
        
        # Identificar períodos de estabilidade
        self.detector.identificar_periodos_estabilidade(min_tamanho=min_tamanho_periodo)
        
        # Calcular métricas temporais
        self.detector.calcular_metricas_temporais()
        
        # Prever próxima mudança
        proxima_mudanca = self.detector.prever_proxima_mudanca()
        
        # Visualizar resultados
        self.detector.visualizar_series_e_mudancas()
        self.detector.visualizar_raizes_por_periodo()
        
        return {
            'pontos_mudanca': self.detector.pontos_mudanca,
            'periodos_estabilidade': self.detector.periodos_estabilidade,
            'proxima_mudanca': proxima_mudanca
        }
    
    def gerar_previsoes_baseadas_em_mudancas(self, n_previsoes=5):
        """
        Gera previsões para jogos futuros baseadas na análise de mudanças temporais.
        
        Args:
            n_previsoes: Número de previsões a gerar.
        
        Returns:
            list: Lista de previsões.
        """
        if not self.detector.periodos_estabilidade:
            print("Execute analisar_mudancas_temporais() primeiro.")
            return []
        
        self.previsoes = []
        
        # Obter o período atual (último período de estabilidade)
        periodo_atual = self.detector.periodos_estabilidade[-1]
        raizes_atuais = periodo_atual['raizes']
        
        # Verificar se estamos próximos de uma mudança
        proxima_mudanca = self.detector.prever_proxima_mudanca()
        proximidade_mudanca = proxima_mudanca.get('sorteios_restantes', float('inf'))
        
        # Estratégia 1: Usar raízes do período atual
        previsao_atual = self._gerar_previsao_baseada_raizes(raizes_atuais)
        self.previsoes.append({
            'metodo': 'raizes_atuais',
            'numeros': previsao_atual,
            'descricao': 'Baseada nos números raízes do período atual'
        })
        
        # Estratégia 2: Se houver períodos anteriores, usar tendência de evolução das raízes
        if len(self.detector.periodos_estabilidade) > 1:
            periodo_anterior = self.detector.periodos_estabilidade[-2]
            raizes_anteriores = periodo_anterior['raizes']
            
            # Calcular tendência de evolução
            tendencia = []
            for i in range(min(len(raizes_atuais), len(raizes_anteriores))):
                delta = raizes_atuais[i] - raizes_anteriores[i]
                tendencia.append(delta)
            
            # Projetar próximas raízes
            proximas_raizes = []
            for i in range(len(raizes_atuais)):
                if i < len(tendencia):
                    # Projetar com tendência
                    nova_raiz = raizes_atuais[i] + tendencia[i]
                    # Garantir que está no intervalo [1, 60]
                    nova_raiz = max(1, min(60, nova_raiz))
                    proximas_raizes.append(int(nova_raiz))
                else:
                    proximas_raizes.append(raizes_atuais[i])
            
            previsao_tendencia = self._gerar_previsao_baseada_raizes(proximas_raizes)
            self.previsoes.append({
                'metodo': 'tendencia_raizes',
                'numeros': previsao_tendencia,
                'descricao': 'Baseada na tendência de evolução dos números raízes'
            })
        
        # Estratégia 3: Se estamos próximos de uma mudança, gerar previsão de transição
        if proximidade_mudanca < 10:
            # Combinar raízes de diferentes períodos
            todas_raizes = []
            for periodo in self.detector.periodos_estabilidade:
                todas_raizes.extend(periodo['raizes'])
            
            # Selecionar raízes únicas mais frequentes
            contador = Counter(todas_raizes)
            raizes_transicao = [r for r, _ in contador.most_common(3)]
            
            previsao_transicao = self._gerar_previsao_baseada_raizes(raizes_transicao)
            self.previsoes.append({
                'metodo': 'transicao',
                'numeros': previsao_transicao,
                'descricao': 'Baseada em possível transição para novo período (mudança próxima)'
            })
        
        # Estratégia 4: Usar características do período atual
        media_pares = periodo_atual['media_pares']
        n_pares = round(media_pares)
        n_impares = 6 - n_pares
        
        # Selecionar números baseados na distribuição de paridade
        todos_numeros = []
        for sorteio in self.detector.sorteios[-20:]:  # Usar sorteios recentes
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
            'descricao': 'Baseada na distribuição de paridade do período atual'
        })
        
        # Estratégia 5: Usar métricas temporais para identificar padrões cíclicos
        if self.detector.metricas_temporais.get('periodicidades'):
            # Verificar se há periodicidade na série 'soma'
            periodicidades_soma = self.detector.metricas_temporais['periodicidades'].get('soma', [])
            
            if periodicidades_soma:
                # Usar o primeiro período detectado
                periodo_ciclo = periodicidades_soma[0]
                
                # Encontrar sorteios em posições cíclicas similares
                posicao_atual = len(self.detector.sorteios) % periodo_ciclo
                sorteios_similares = []
                
                for i in range(len(self.detector.sorteios)):
                    if i % periodo_ciclo == posicao_atual:
                        sorteios_similares.append(self.detector.sorteios[i])
                
                if sorteios_similares:
                    # Contar frequência dos números em sorteios similares
                    contador_ciclico = Counter()
                    for sorteio in sorteios_similares:
                        for num in sorteio:
                            contador_ciclico[num] += 1
                    
                    # Selecionar os mais frequentes
                    numeros_ciclicos = [num for num, _ in contador_ciclico.most_common(6)]
                    
                    previsao_ciclica = sorted(numeros_ciclicos)
                    self.previsoes.append({
                        'metodo': 'padrao_ciclico',
                        'numeros': previsao_ciclica,
                        'descricao': 'Baseada em padrões cíclicos detectados nas séries temporais'
                    })
        
        # Limitar ao número solicitado
        self.previsoes = self.previsoes[:n_previsoes]
        
        print(f"\nGeradas {len(self.previsoes)} previsões baseadas em mudanças temporais:")
        for i, prev in enumerate(self.previsoes, 1):
            print(f"{i}. Método: {prev['metodo']} - Números: {prev['numeros']}")
            print(f"   {prev['descricao']}")
        
        return self.previsoes
    
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
    
    def salvar_previsoes(self, arquivo="previsoes_mudancas_temporais.json"):
        """
        Salva as previsões em um arquivo JSON.
        
        Args:
            arquivo: Nome do arquivo para salvar.
        
        Returns:
            bool: True se as previsões foram salvas com sucesso, False caso contrário.
        """
        if not self.previsoes:
            print("Nenhuma previsão para salvar. Execute gerar_previsoes_baseadas_em_mudancas() primeiro.")
            return False
        
        try:
            data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            dados_saida = {
                "data_geracao": data_atual,
                "total_sorteios_analisados": len(self.detector.sorteios),
                "previsoes": self.previsoes
            }
            
            # Adicionar informações sobre períodos de estabilidade
            if self.detector.periodos_estabilidade:
                dados_saida["info_periodos"] = {
                    "total_periodos": len(self.detector.periodos_estabilidade),
                    "periodo_atual": {
                        "inicio": self.detector.periodos_estabilidade[-1]['inicio'],
                        "tamanho": self.detector.periodos_estabilidade[-1]['tamanho'],
                        "raizes": self.detector.periodos_estabilidade[-1]['raizes']
                    }
                }
            
            # Adicionar informação sobre próxima mudança prevista
            proxima_mudanca = self.detector.prever_proxima_mudanca()
            if proxima_mudanca:
                dados_saida["proxima_mudanca"] = proxima_mudanca
            
            with open(arquivo, 'w') as f:
                json.dump(dados_saida, f, indent=2)
            
            print(f"Previsões salvas com sucesso em {arquivo}")
            return True
        except Exception as e:
            print(f"Erro ao salvar previsões: {e}")
            return False


def testar_detector_mudancas():
    """
    Função para testar o detector de mudanças temporais.
    """
    print("\n===== Teste de Detecção de Mudanças Temporais =====")
    
    # Verificar se o arquivo de dados existe
    arquivo_padrao = "megasena_dados.json"
    if not os.path.exists(arquivo_padrao):
        print(f"Arquivo {arquivo_padrao} não encontrado. Criando dados de teste...")
        
        # Criar dados de teste
        dados_teste = {}
        for i in range(1, 201):
            # Gerar sorteios com mudança de padrão a cada 50 sorteios
            if i <= 50:
                # Período 1: Mais números baixos
                sorteio = sorted(np.random.choice(range(1, 31), 4, replace=False).tolist() + 
                                np.random.choice(range(31, 61), 2, replace=False).tolist())
            elif i <= 100:
                # Período 2: Mais números altos
                sorteio = sorted(np.random.choice(range(1, 31), 2, replace=False).tolist() + 
                                np.random.choice(range(31, 61), 4, replace=False).tolist())
            elif i <= 150:
                # Período 3: Mais números pares
                pares = list(range(2, 61, 2))
                impares = list(range(1, 61, 2))
                sorteio = sorted(np.random.choice(pares, 4, replace=False).tolist() + 
                                np.random.choice(impares, 2, replace=False).tolist())
            else:
                # Período 4: Mais números ímpares
                pares = list(range(2, 61, 2))
                impares = list(range(1, 61, 2))
                sorteio = sorted(np.random.choice(pares, 2, replace=False).tolist() + 
                                np.random.choice(impares, 4, replace=False).tolist())
            
            dados_teste[str(i)] = [str(n) for n in sorteio]
        
        # Salvar dados de teste
        with open("dados_teste_mudancas.json", 'w') as f:
            json.dump(dados_teste, f)
        
        arquivo_padrao = "dados_teste_mudancas.json"
    
    # Criar analisador
    analisador = AnalisadorMudancasTemporais()
    
    # Carregar dados
    analisador.carregar_dados(arquivo_padrao)
    
    # Analisar mudanças temporais
    analisador.analisar_mudancas_temporais()
    
    # Gerar previsões
    previsoes = analisador.gerar_previsoes_baseadas_em_mudancas(n_previsoes=3)
    
    # Salvar previsões
    analisador.salvar_previsoes("teste_previsoes_mudancas.json")
    
    print("\n===== Teste concluído =====")


if __name__ == "__main__":
    testar_detector_mudancas()

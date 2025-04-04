import os
import json
import base64
import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("megasena_web.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("megasena_web")

class MegaSenaPredictorWeb:
    def __init__(self):
        """
        Inicializa o preditor da Mega Sena para web.
        """
        self.diretorio_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")
        self.arquivo_dados = os.path.join(self.diretorio_dados, "mega_sena_dados.json")
        self.dados_carregados = False
        self.sorteios = []
        
        # Criar diretório de dados se não existir
        os.makedirs(self.diretorio_dados, exist_ok=True)
        
        # Tentar carregar dados existentes
        self.carregar_dados()
        
        logger.info(f"MegaSenaPredictorWeb inicializado. Diretório de dados: {self.diretorio_dados}")
    
    def carregar_dados(self):
        """Carrega os dados históricos da Mega Sena."""
        try:
            if os.path.exists(self.arquivo_dados):
                with open(self.arquivo_dados, 'r') as f:
                    self.sorteios = json.load(f)
                self.dados_carregados = True
                logger.info(f"Dados carregados com sucesso. Total de sorteios: {len(self.sorteios)}")
                return True
            else:
                logger.warning(f"Arquivo de dados não encontrado: {self.arquivo_dados}")
                return False
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            return False
    
    def baixar_dados(self):
        """Baixa os dados históricos da Mega Sena."""
        try:
            # Em uma implementação real, isso faria uma requisição para obter os dados
            # Aqui, vamos simular com alguns dados de exemplo
            
            # Verificar se já temos dados
            if self.dados_carregados and len(self.sorteios) > 0:
                logger.info("Dados já carregados. Atualizando...")
                return True
            
            # Criar alguns dados de exemplo
            self.sorteios = [
                {"concurso": 1, "data": "11/03/1996", "dezenas": [4, 5, 30, 33, 41, 52]},
                {"concurso": 2, "data": "18/03/1996", "dezenas": [9, 37, 39, 41, 43, 49]},
                {"concurso": 3, "data": "25/03/1996", "dezenas": [10, 11, 29, 30, 36, 47]},
                {"concurso": 4, "data": "01/04/1996", "dezenas": [3, 11, 18, 29, 47, 60]},
                {"concurso": 5, "data": "08/04/1996", "dezenas": [5, 9, 13, 16, 41, 45]}
            ]
            
            # Salvar dados
            with open(self.arquivo_dados, 'w') as f:
                json.dump(self.sorteios, f, indent=2)
            
            self.dados_carregados = True
            logger.info(f"Dados baixados e salvos com sucesso. Total de sorteios: {len(self.sorteios)}")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao baixar dados: {e}")
            return False
    
    def adicionar_sorteio(self, numeros):
        """Adiciona um novo sorteio aos dados."""
        try:
            if not self.dados_carregados:
                if not self.carregar_dados():
                    logger.warning("Não foi possível carregar dados existentes.")
            
            # Verificar se os números são válidos
            if len(numeros) != 6:
                logger.warning(f"Número inválido de dezenas: {len(numeros)}")
                return False
            
            for num in numeros:
                if num < 1 or num > 60:
                    logger.warning(f"Dezena inválida: {num}")
                    return False
            
            # Determinar o próximo número de concurso
            proximo_concurso = 1
            if self.sorteios:
                proximo_concurso = max(sorteio.get("concurso", 0) for sorteio in self.sorteios) + 1
            
            # Criar novo sorteio
            novo_sorteio = {
                "concurso": proximo_concurso,
                "data": "01/01/2025",  # Data fictícia
                "dezenas": sorted(numeros)
            }
            
            # Adicionar ao conjunto de dados
            self.sorteios.append(novo_sorteio)
            
            # Salvar dados
            with open(self.arquivo_dados, 'w') as f:
                json.dump(self.sorteios, f, indent=2)
            
            logger.info(f"Novo sorteio adicionado: {novo_sorteio}")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao adicionar sorteio: {e}")
            return False
    
    def obter_estatisticas(self):
        """Obtém estatísticas dos dados históricos."""
        try:
            if not self.dados_carregados:
                if not self.carregar_dados():
                    logger.warning("Não foi possível carregar dados para estatísticas.")
                    return None
            
            if not self.sorteios:
                logger.warning("Nenhum dado disponível para estatísticas.")
                return None
            
            # Extrair todas as dezenas
            todas_dezenas = []
            for sorteio in self.sorteios:
                todas_dezenas.extend(sorteio.get("dezenas", []))
            
            # Contar frequência de cada número
            frequencia = {}
            for i in range(1, 61):
                frequencia[i] = todas_dezenas.count(i)
            
            # Ordenar por frequência
            frequencia_ordenada = sorted(frequencia.items(), key=lambda x: x[1], reverse=True)
            
            # Obter números mais e menos frequentes
            mais_frequentes = frequencia_ordenada[:10]
            menos_frequentes = frequencia_ordenada[-10:]
            
            # Calcular distribuição de paridade
            total_numeros = len(todas_dezenas)
            numeros_pares = sum(1 for num in todas_dezenas if num % 2 == 0)
            numeros_impares = total_numeros - numeros_pares
            
            percentual_pares = (numeros_pares / total_numeros) * 100
            percentual_impares = (numeros_impares / total_numeros) * 100
            
            # Calcular distribuição por dezenas
            dezenas = ["01-10", "11-20", "21-30", "31-40", "41-50", "51-60"]
            contagem_dezenas = [0, 0, 0, 0, 0, 0]
            
            for num in todas_dezenas:
                idx = (num - 1) // 10
                contagem_dezenas[idx] += 1
            
            percentuais_dezenas = [(count / total_numeros) * 100 for count in contagem_dezenas]
            
            # Gerar gráfico de frequência
            plt.figure(figsize=(12, 6))
            nums = list(range(1, 61))
            freqs = [frequencia[num] for num in nums]
            
            plt.bar(nums, freqs, color='blue', alpha=0.7)
            plt.xlabel('Número')
            plt.ylabel('Frequência')
            plt.title('Frequência dos Números na Mega Sena')
            plt.xticks(range(0, 61, 5))
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Converter gráfico para base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()
            
            # Montar resultado
            resultado = {
                "total_sorteios": len(self.sorteios),
                "mais_frequentes": mais_frequentes,
                "menos_frequentes": menos_frequentes,
                "distribuicao_paridade": {
                    "pares": numeros_pares,
                    "impares": numeros_impares,
                    "percentual_pares": percentual_pares,
                    "percentual_impares": percentual_impares
                },
                "distribuicao_dezenas": {
                    "dezenas": dezenas,
                    "contagens": contagem_dezenas,
                    "percentuais": percentuais_dezenas
                },
                "grafico_frequencia": grafico_base64
            }
            
            return resultado
        
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return None
    
    def detectar_numeros_raizes(self, tamanho_janela=50, n_raizes=3):
        """Detecta possíveis números raízes nos dados históricos."""
        try:
            if not self.dados_carregados:
                if not self.carregar_dados():
                    logger.warning("Não foi possível carregar dados para detecção de raízes.")
                    return None
            
            if not self.sorteios or len(self.sorteios) < tamanho_janela:
                logger.warning(f"Dados insuficientes para detecção de raízes. Necessário: {tamanho_janela}, Disponível: {len(self.sorteios)}")
                return None
            
            # Extrair dezenas de todos os sorteios
            dezenas_sorteios = [sorteio.get("dezenas", []) for sorteio in self.sorteios]
            
            # Criar janelas deslizantes
            janelas = []
            for i in range(len(dezenas_sorteios) - tamanho_janela + 1):
                janela = dezenas_sorteios[i:i+tamanho_janela]
                janelas.append(janela)
            
            # Detectar números raízes para cada janela
            numeros_raizes = []
            for idx, janela in enumerate(janelas):
                # Contar frequência de cada número na janela
                frequencia = {}
                for dezenas in janela:
                    for num in dezenas:
                        frequencia[num] = frequencia.get(num, 0) + 1
                
                # Ordenar por frequência
                frequencia_ordenada = sorted(frequencia.items(), key=lambda x: x[1], reverse=True)
                
                # Obter os n_raizes números mais frequentes
                raizes = [num for num, _ in frequencia_ordenada[:n_raizes]]
                
                numeros_raizes.append({
                    "janela_idx": idx,
                    "inicio": idx,
                    "fim": idx + tamanho_janela - 1,
                    "raizes": raizes
                })
            
            # Detectar pontos de mudança
            pontos_mudanca = []
            for i in range(1, len(numeros_raizes)):
                raizes_anterior = set(numeros_raizes[i-1]["raizes"])
                raizes_atual = set(numeros_raizes[i]["raizes"])
                
                # Calcular diferença entre conjuntos de raízes
                diferenca = 1 - len(raizes_anterior.intersection(raizes_atual)) / n_raizes
                
                # Se a diferença for significativa, considerar como ponto de mudança
                if diferenca > 0.5:  # Mais de 50% de mudança
                    pontos_mudanca.append({
                        "janela_idx": i,
                        "inicio_sorteio": numeros_raizes[i]["inicio"],
                        "raizes_antes": list(raizes_anterior),
                        "raizes_depois": list(raizes_atual),
                        "diferenca": diferenca
                    })
            
            # Gerar gráfico de evolução das raízes
            plt.figure(figsize=(12, 6))
            
            # Plotar evolução de cada raiz
            for i in range(n_raizes):
                valores = [r["raizes"][i] if i < len(r["raizes"]) else None for r in numeros_raizes]
                indices = [r["janela_idx"] for r in numeros_raizes]
                plt.plot(indices, valores, marker='o', label=f'Raiz {i+1}')
            
            # Marcar pontos de mudança
            for ponto in pontos_mudanca:
                plt.axvline(x=ponto["janela_idx"], color='r', linestyle='--', alpha=0.5)
            
            plt.xlabel('Índice da Janela')
            plt.ylabel('Valor da Raiz')
            plt.title('Evolução dos Números Raízes ao Longo do Tempo')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Converter gráfico para base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()
            
            # Obter raízes mais recentes
            raizes_recentes = numeros_raizes[-1]["raizes"] if numeros_raizes else []
            
            # Montar resultado
            resultado = {
                "total_janelas": len(janelas),
                "tamanho_janela": tamanho_janela,
                "n_raizes": n_raizes,
                "numeros_raizes": numeros_raizes,
                "pontos_mudanca": pontos_mudanca,
                "total_pontos_mudanca": len(pontos_mudanca),
                "raizes_recentes": raizes_recentes,
                "grafico_evolucao": grafico_base64
            }
            
            return resultado
        
        except Exception as e:
            logger.error(f"Erro ao detectar números raízes: {e}")
            return None
    
    def gerar_previsoes(self, n_previsoes=5):
        """Gera previsões para jogos futuros."""
        try:
            if not self.dados_carregados:
                if not self.carregar_dados():
                    logger.warning("Não foi possível carregar dados para previsões.")
                    return None
            
            if not self.sorteios:
                logger.warning("Nenhum dado disponível para previsões.")
                return None
            
            # Implementar diferentes métodos de previsão
            previsoes = []
            
            # Método 1: Baseado em frequência
            try:
                # Extrair todas as dezenas
                todas_dezenas = []
                for sorteio in self.sorteios:
                    todas_dezenas.extend(sorteio.get("dezenas", []))
                
                # Contar frequência de cada número
                frequencia = {}
                for i in range(1, 61):
                    frequencia[i] = todas_dezenas.count(i)
                
                # Ordenar por frequência
                frequencia_ordenada = sorted(frequencia.items(), key=lambda x: x[1], reverse=True)
                
                # Selecionar os 6 números mais frequentes
                numeros_frequentes = [num for num, _ in frequencia_ordenada[:6]]
                
                previsoes.append({
                    "metodo": "Frequência",
                    "numeros": numeros_frequentes,
                    "confianca": 0.65,
                    "descricao": "Baseado nos números que mais aparecem historicamente."
                })
            except Exception as e:
                logger.error(f"Erro no método de frequência: {e}")
            
            # Método 2: Baseado em paridade
            try:
                # Analisar distribuição de paridade nos últimos sorteios
                ultimos_sorteios = self.sorteios[-20:]
                
                # Contar números pares e ímpares em cada sorteio
                distribuicao = []
                for sorteio in ultimos_sorteios:
                    dezenas = sorteio.get("dezenas", [])
                    pares = sum(1 for num in dezenas if num % 2 == 0)
                    impares = 6 - pares
                    distribuicao.append((pares, impares))
                
                # Encontrar a distribuição mais comum
                contagem = {}
        
(Content truncated due to size limit. Use line ranges to read in chunks)
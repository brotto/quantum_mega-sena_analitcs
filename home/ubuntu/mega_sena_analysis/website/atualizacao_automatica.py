import os
import json
import time
import logging
import requests
import schedule
from datetime import datetime
from threading import Thread

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("atualizacao_automatica.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("atualizacao_automatica")

class AtualizadorMegaSena:
    def __init__(self, diretorio_dados, url_api=None):
        """
        Inicializa o atualizador automático da Mega Sena.
        
        Args:
            diretorio_dados: Diretório onde os dados serão armazenados
            url_api: URL da API da Loteria Caixa (opcional)
        """
        self.diretorio_dados = diretorio_dados
        self.url_api = url_api or "https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena"
        self.arquivo_dados = os.path.join(diretorio_dados, "mega_sena_dados.json")
        self.arquivo_ultimo_sorteio = os.path.join(diretorio_dados, "ultimo_sorteio.txt")
        self.thread_atualizacao = None
        self.executando = False
        
        # Criar diretório de dados se não existir
        os.makedirs(diretorio_dados, exist_ok=True)
        
        logger.info(f"Atualizador inicializado. Diretório de dados: {diretorio_dados}")
    
    def iniciar_atualizacao_programada(self):
        """Inicia a atualização programada em uma thread separada."""
        if self.thread_atualizacao and self.thread_atualizacao.is_alive():
            logger.warning("Atualização já está em execução.")
            return False
        
        self.executando = True
        self.thread_atualizacao = Thread(target=self._executar_atualizacao_programada)
        self.thread_atualizacao.daemon = True
        self.thread_atualizacao.start()
        
        logger.info("Atualização programada iniciada.")
        return True
    
    def parar_atualizacao_programada(self):
        """Para a atualização programada."""
        self.executando = False
        if self.thread_atualizacao and self.thread_atualizacao.is_alive():
            self.thread_atualizacao.join(timeout=5)
            logger.info("Atualização programada interrompida.")
            return True
        
        logger.warning("Nenhuma atualização em execução para interromper.")
        return False
    
    def _executar_atualizacao_programada(self):
        """Executa a atualização programada em segundo plano."""
        # Programar atualizações
        # - Diariamente às 21:00 (após os sorteios regulares)
        # - Semanalmente aos domingos às 00:00 (verificação completa)
        schedule.every().day.at("21:00").do(self.verificar_novos_sorteios)
        schedule.every().sunday.at("00:00").do(self.atualizar_dados_completos)
        
        # Executar uma verificação inicial
        self.verificar_novos_sorteios()
        
        # Loop principal
        while self.executando:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto
    
    def obter_ultimo_sorteio_salvo(self):
        """Obtém o número do último sorteio salvo localmente."""
        try:
            if os.path.exists(self.arquivo_ultimo_sorteio):
                with open(self.arquivo_ultimo_sorteio, 'r') as f:
                    return int(f.read().strip())
            return 0
        except Exception as e:
            logger.error(f"Erro ao obter último sorteio salvo: {e}")
            return 0
    
    def salvar_ultimo_sorteio(self, numero_sorteio):
        """Salva o número do último sorteio."""
        try:
            with open(self.arquivo_ultimo_sorteio, 'w') as f:
                f.write(str(numero_sorteio))
            logger.info(f"Último sorteio atualizado: {numero_sorteio}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar último sorteio: {e}")
            return False
    
    def obter_dados_api(self):
        """Obtém os dados mais recentes da API da Loteria Caixa."""
        try:
            logger.info(f"Consultando API: {self.url_api}")
            response = requests.get(self.url_api, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter dados da API: {e}")
            return None
    
    def verificar_novos_sorteios(self):
        """Verifica se há novos sorteios e atualiza os dados."""
        logger.info("Verificando novos sorteios...")
        
        # Obter último sorteio salvo
        ultimo_sorteio_salvo = self.obter_ultimo_sorteio_salvo()
        
        # Obter dados da API
        dados_api = self.obter_dados_api()
        if not dados_api:
            logger.warning("Não foi possível obter dados da API.")
            return False
        
        # Verificar número do último sorteio
        try:
            numero_concurso = int(dados_api.get('numero', 0))
            if numero_concurso <= ultimo_sorteio_salvo:
                logger.info(f"Nenhum novo sorteio encontrado. Último: {ultimo_sorteio_salvo}")
                return False
            
            # Extrair dados do sorteio
            dezenas = dados_api.get('dezenasSorteadasOrdemSorteio', [])
            data_sorteio = dados_api.get('dataApuracao', '')
            
            if not dezenas or len(dezenas) != 6:
                logger.warning(f"Dados de sorteio inválidos: {dezenas}")
                return False
            
            # Converter dezenas para inteiros
            dezenas = [int(d) for d in dezenas]
            
            # Adicionar novo sorteio aos dados
            self.adicionar_sorteio(numero_concurso, dezenas, data_sorteio)
            
            # Atualizar último sorteio
            self.salvar_ultimo_sorteio(numero_concurso)
            
            logger.info(f"Novo sorteio adicionado: {numero_concurso} - {dezenas}")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao processar dados do sorteio: {e}")
            return False
    
    def adicionar_sorteio(self, numero_concurso, dezenas, data_sorteio):
        """Adiciona um novo sorteio aos dados salvos."""
        try:
            # Carregar dados existentes
            dados = self.carregar_dados()
            
            # Adicionar novo sorteio
            novo_sorteio = {
                "concurso": numero_concurso,
                "data": data_sorteio,
                "dezenas": dezenas
            }
            
            # Verificar se o sorteio já existe
            for i, sorteio in enumerate(dados):
                if sorteio.get("concurso") == numero_concurso:
                    # Atualizar sorteio existente
                    dados[i] = novo_sorteio
                    logger.info(f"Sorteio {numero_concurso} atualizado.")
                    break
            else:
                # Adicionar novo sorteio
                dados.append(novo_sorteio)
                logger.info(f"Sorteio {numero_concurso} adicionado.")
            
            # Ordenar por número do concurso
            dados.sort(key=lambda x: x.get("concurso", 0))
            
            # Salvar dados
            self.salvar_dados(dados)
            
            return True
        
        except Exception as e:
            logger.error(f"Erro ao adicionar sorteio: {e}")
            return False
    
    def carregar_dados(self):
        """Carrega os dados salvos."""
        try:
            if os.path.exists(self.arquivo_dados):
                with open(self.arquivo_dados, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            return []
    
    def salvar_dados(self, dados):
        """Salva os dados."""
        try:
            with open(self.arquivo_dados, 'w') as f:
                json.dump(dados, f, indent=2)
            logger.info(f"Dados salvos com sucesso. Total de sorteios: {len(dados)}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {e}")
            return False
    
    def atualizar_dados_completos(self):
        """Atualiza todos os dados históricos da Mega Sena."""
        logger.info("Iniciando atualização completa dos dados...")
        
        try:
            # Implementar lógica para obter todos os dados históricos
            # Esta é uma implementação simplificada que apenas verifica o último sorteio
            # Em uma implementação real, seria necessário obter todos os sorteios
            
            return self.verificar_novos_sorteios()
            
        except Exception as e:
            logger.error(f"Erro na atualização completa: {e}")
            return False

# Função para iniciar o atualizador como um serviço
def iniciar_servico_atualizacao(diretorio_dados):
    """Inicia o serviço de atualização automática."""
    atualizador = AtualizadorMegaSena(diretorio_dados)
    atualizador.iniciar_atualizacao_programada()
    return atualizador

# Função para executar uma atualização imediata
def atualizar_agora(diretorio_dados):
    """Executa uma atualização imediata."""
    atualizador = AtualizadorMegaSena(diretorio_dados)
    return atualizador.verificar_novos_sorteios()

if __name__ == "__main__":
    # Diretório padrão para dados
    diretorio_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")
    
    # Iniciar serviço de atualização
    atualizador = iniciar_servico_atualizacao(diretorio_dados)
    
    # Manter o script em execução
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        atualizador.parar_atualizacao_programada()
        logger.info("Serviço de atualização encerrado pelo usuário.")

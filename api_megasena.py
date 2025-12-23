from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import Optional
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Quantum Mega Sena Data API",
    description="API para consulta de dados históricos da Mega Sena",
    version="1.0.0"
)

# CORS - permite que n8n e outras aplicações consumam a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração do banco via variáveis de ambiente
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "megasena"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

def get_db_connection():
    """Cria conexão com o banco PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar no banco: {e}")
        raise HTTPException(status_code=500, detail="Erro ao conectar no banco de dados")

@app.get("/")
def root():
    """Endpoint raiz - verificação de saúde da API"""
    return {
        "status": "online",
        "message": "Quantum Mega Sena Data API 🎲⚛️",
        "version": "1.0.0",
        "endpoints": {
            "/sorteios/todos": "Retorna todos os sorteios",
            "/sorteios/ultimos/{n}": "Retorna os últimos N sorteios",
            "/sorteios/concurso/{numero}": "Retorna um sorteio específico",
            "/sorteios/json": "Retorna dados no formato JSON compatível com o projeto"
        }
    }

@app.get("/health")
def health_check():
    """Verifica se a API e o banco estão funcionando"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check falhou: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@app.get("/sorteios/todos")
def todos_sorteios(limit: Optional[int] = None):
    """
    Retorna todos os sorteios (ou limitado por quantidade)
    
    Args:
        limit: Número máximo de sorteios a retornar (opcional)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT concurso, data_sorteio, 
                   dezena_1, dezena_2, dezena_3, 
                   dezena_4, dezena_5, dezena_6
            FROM sorteios_megasena
            ORDER BY concurso DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        
        sorteios = []
        for row in resultados:
            sorteios.append({
                "concurso": row["concurso"],
                "data": str(row["data_sorteio"]),
                "dezenas": [
                    row["dezena_1"], row["dezena_2"], row["dezena_3"],
                    row["dezena_4"], row["dezena_5"], row["dezena_6"]
                ]
            })
        
        return {
            "total": len(sorteios),
            "sorteios": sorteios
        }
    
    except Exception as e:
        logger.error(f"Erro ao buscar todos os sorteios: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sorteios/ultimos/{n}")
def ultimos_sorteios(n: int):
    """
    Retorna os últimos N sorteios
    
    Args:
        n: Número de sorteios a retornar
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT concurso, data_sorteio, 
                   dezena_1, dezena_2, dezena_3, 
                   dezena_4, dezena_5, dezena_6
            FROM sorteios_megasena
            ORDER BY concurso DESC
            LIMIT %s
        """, (n,))
        
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        
        sorteios = []
        for row in resultados:
            sorteios.append({
                "concurso": row["concurso"],
                "data": str(row["data_sorteio"]),
                "dezenas": [
                    row["dezena_1"], row["dezena_2"], row["dezena_3"],
                    row["dezena_4"], row["dezena_5"], row["dezena_6"]
                ]
            })
        
        return {
            "total": len(sorteios),
            "sorteios": sorteios
        }
    
    except Exception as e:
        logger.error(f"Erro ao buscar últimos sorteios: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sorteios/concurso/{numero}")
def sorteio_por_concurso(numero: int):
    """
    Retorna um sorteio específico pelo número do concurso
    
    Args:
        numero: Número do concurso
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT concurso, data_sorteio, 
                   dezena_1, dezena_2, dezena_3, 
                   dezena_4, dezena_5, dezena_6
            FROM sorteios_megasena
            WHERE concurso = %s
        """, (numero,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return {
                "concurso": row["concurso"],
                "data": str(row["data_sorteio"]),
                "dezenas": [
                    row["dezena_1"], row["dezena_2"], row["dezena_3"],
                    row["dezena_4"], row["dezena_5"], row["dezena_6"]
                ]
            }
        else:
            raise HTTPException(status_code=404, detail="Concurso não encontrado")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar concurso: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sorteios/json")
def sorteios_formato_json():
    """
    Retorna os dados no formato JSON compatível com o mega_sena_predictor.py
    Formato: { "1": ["04", "05", "30", "33", "41", "52"], "2": [...], ... }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT concurso, 
                   dezena_1, dezena_2, dezena_3, 
                   dezena_4, dezena_5, dezena_6
            FROM sorteios_megasena
            ORDER BY concurso ASC
        """)
        
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Formatar no padrão do projeto
        dados_formatados = {}
        for row in resultados:
            concurso = str(row["concurso"])
            dezenas = [
                f"{row['dezena_1']:02d}",
                f"{row['dezena_2']:02d}",
                f"{row['dezena_3']:02d}",
                f"{row['dezena_4']:02d}",
                f"{row['dezena_5']:02d}",
                f"{row['dezena_6']:02d}"
            ]
            dados_formatados[concurso] = dezenas
        
        return dados_formatados
    
    except Exception as e:
        logger.error(f"Erro ao buscar dados em formato JSON: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/estatisticas/frequencia")
def estatisticas_frequencia():
    """Retorna a frequência de cada número nos sorteios"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Contar frequência de cada número
        frequencias = {}
        for i in range(1, 61):
            cursor.execute(f"""
                SELECT COUNT(*) as freq FROM sorteios_megasena
                WHERE dezena_1 = %s OR dezena_2 = %s OR dezena_3 = %s
                   OR dezena_4 = %s OR dezena_5 = %s OR dezena_6 = %s
            """, (i, i, i, i, i, i))
            
            result = cursor.fetchone()
            frequencias[i] = result["freq"]
        
        cursor.close()
        conn.close()
        
        # Ordenar por frequência
        frequencias_ordenadas = sorted(
            frequencias.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return {
            "frequencias": frequencias,
            "mais_frequentes": frequencias_ordenadas[:10],
            "menos_frequentes": frequencias_ordenadas[-10:]
        }
    
    except Exception as e:
        logger.error(f"Erro ao calcular frequências: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

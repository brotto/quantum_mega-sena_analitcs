import sys
sys.path.append('/home/ubuntu/mega_sena_analysis')
from website.app import MegaSenaPredictorWeb
import json
import numpy as np

# Função para converter tipos NumPy para tipos Python nativos
def converter_para_serializavel(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, list):
        return [converter_para_serializavel(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: converter_para_serializavel(value) for key, value in obj.items()}
    else:
        return obj

# Inicializar o preditor
predictor = MegaSenaPredictorWeb()

# Gerar previsões
resultado = predictor.gerar_previsoes(5)

# Extrair as previsões
previsoes = resultado.get('previsoes', [])

# Converter para tipos serializáveis
previsoes_serializaveis = converter_para_serializavel(previsoes)

# Salvar as previsões em um arquivo JSON para análise
with open('/home/ubuntu/mega_sena_analysis/previsoes_geradas.json', 'w') as f:
    json.dump(previsoes_serializaveis, f, indent=2)

# Imprimir as previsões de forma legível
print("PREVISÕES GERADAS:")
print("-----------------")
for i, previsao in enumerate(previsoes, 1):
    print(f"Previsão {i}:")
    print(f"  Método: {previsao.get('metodo', 'N/A')}")
    print(f"  Números: {previsao.get('numeros', [])}")
    print(f"  Confiança: {previsao.get('confianca', 0)*100:.2f}%")
    print(f"  Descrição: {previsao.get('descricao', 'N/A')}")
    print()

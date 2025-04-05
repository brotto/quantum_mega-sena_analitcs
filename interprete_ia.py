# interprete_ia.py

import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def interpretar_estabilidade_via_ia(periodo_atual, total_estaveis):
    if not periodo_atual:
        return "Não foi possível identificar um período estável no momento. Aguarde novos sorteios para uma interpretação mais confiável."

    contexto = f"""
    Você é um analista inteligente de padrões da Mega Sena. O sistema detectou um total de {total_estaveis} períodos estáveis.
    O período atual começou no sorteio {periodo_atual['inicio']} e já dura {periodo_atual['tamanho']} sorteios consecutivos.
    Avalie se esse é um bom momento para aplicar estratégias baseadas em números raízes, explique com clareza e objetividade.
    """

    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um especialista em análise estatística da Mega Sena, explicando padrões ao usuário de forma clara."},
            {"role": "user", "content": contexto}
        ],
        temperature=0.6
    )

    return resposta["choices"][0]["message"]["content"]
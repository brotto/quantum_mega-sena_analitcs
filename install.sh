#!/bin/bash

# Script de instalação para o MegaSenaPredictor
# Este script instala todas as dependências necessárias e configura o ambiente

echo "=== Instalando MegaSenaPredictor ==="
echo "Verificando requisitos..."

# Verificar se Python está instalado
if command -v python3 &>/dev/null; then
    python_version=$(python3 --version)
    echo "✓ $python_version encontrado"
else
    echo "✗ Python 3 não encontrado. Por favor, instale o Python 3.7 ou superior."
    exit 1
fi

# Criar ambiente virtual
echo "Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
echo "Instalando dependências..."
pip install numpy matplotlib pandas requests tqdm
echo "✓ Dependências básicas instaladas"

# Instalar PennyLane (opcional)
echo "Deseja instalar PennyLane para simulação quântica? (s/n)"
read -r install_pennylane

if [[ $install_pennylane == "s" || $install_pennylane == "S" ]]; then
    echo "Instalando PennyLane..."
    pip install pennylane
    echo "✓ PennyLane instalado"
else
    echo "Simulação quântica não será disponível."
fi

# Criar diretórios necessários
echo "Configurando diretórios..."
mkdir -p data
mkdir -p output

echo "✓ Diretórios criados"

# Verificar se os arquivos principais existem
echo "Verificando arquivos do sistema..."
files_ok=true

for file in mega_sena_predictor.py detector_numeros_raizes.py simulacao_quantica_avancada.py detector_mudancas_temporais.py validador_modelos.py gerador_previsoes_finais.py README.md; do
    if [ -f "$file" ]; then
        echo "✓ $file encontrado"
    else
        echo "✗ $file não encontrado"
        files_ok=false
    fi
done

if [ "$files_ok" = false ]; then
    echo "Alguns arquivos estão faltando. Verifique se todos os arquivos foram baixados corretamente."
else
    echo "✓ Todos os arquivos necessários estão presentes"
fi

# Baixar dados históricos
echo "Deseja baixar os dados históricos da Mega Sena agora? (s/n)"
read -r download_data

if [[ $download_data == "s" || $download_data == "S" ]]; then
    echo "Baixando dados históricos..."
    python3 mega_sena_predictor.py --download
    echo "✓ Dados históricos baixados"
else
    echo "Você pode baixar os dados mais tarde usando 'python3 mega_sena_predictor.py --download'"
fi

echo ""
echo "=== Instalação concluída ==="
echo "Para iniciar o MegaSenaPredictor, execute:"
echo "source venv/bin/activate  # Ativar ambiente virtual"
echo "python3 mega_sena_predictor.py  # Iniciar o programa"
echo ""
echo "Consulte o README.md para mais informações sobre como usar o sistema."

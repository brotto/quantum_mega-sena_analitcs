#!/bin/bash

# Script para fazer commit e push das alterações para o GitHub

echo "🚀 Preparando deploy para Easypanel..."
echo ""

# Adicionar todos os arquivos novos
git add api_megasena.py
git add Dockerfile
git add requirements.txt
git add .env.example
git add DEPLOY.md
git add database_setup.sql
git add deploy_to_easypanel.sh

echo "✅ Arquivos adicionados ao Git"
echo ""

# Fazer commit
git commit -m "feat: Adicionar API FastAPI e configuração para deploy no Easypanel

- Criar api_megasena.py com endpoints para consulta de sorteios
- Adicionar Dockerfile para build no Easypanel
- Atualizar requirements.txt com FastAPI, uvicorn e psycopg2
- Criar .env.example com template de variáveis de ambiente
- Adicionar DEPLOY.md com guia completo de deploy
- Criar database_setup.sql para configuração do PostgreSQL"

echo "✅ Commit realizado"
echo ""

# Push para o GitHub
git push origin main

echo ""
echo "🎉 Deploy pronto! Agora você pode:"
echo "1. Acessar o Easypanel"
echo "2. Criar novo App → Git Repository"
echo "3. Conectar: https://github.com/brotto/quantum_mega-sena_analitcs"
echo "4. Configurar variáveis de ambiente (veja DEPLOY.md)"
echo "5. Deploy automático!"
echo ""
echo "📚 Leia o arquivo DEPLOY.md para instruções detalhadas"

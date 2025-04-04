#!/bin/bash

echo "Fazendo commit e push do projeto..."

# Adiciona tudo
git add .

# Cria um commit com mensagem automática (ou personalize)
git commit -m "Atualização automática do projeto MegaSenaPredictor"

# Push para o GitHub
git push origin main

echo "Push realizado com sucesso!"
# 🚀 Deploy no Easypanel - Quantum Mega Sena API

## Pré-requisitos

1. **Banco de dados PostgreSQL** configurado no Easypanel
2. **Tabela criada** com a seguinte estrutura:

```sql
CREATE TABLE sorteios_megasena (
    id SERIAL PRIMARY KEY,
    concurso INTEGER UNIQUE NOT NULL,
    data_sorteio DATE NOT NULL,
    dezena_1 INTEGER NOT NULL,
    dezena_2 INTEGER NOT NULL,
    dezena_3 INTEGER NOT NULL,
    dezena_4 INTEGER NOT NULL,
    dezena_5 INTEGER NOT NULL,
    dezena_6 INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Passo a Passo no Easypanel

### 1. Criar App

1. Acesse o Easypanel
2. Clique em **"+ Create"** → **"App"**
3. Selecione **"Git Repository"**
4. Conecte o repositório: `https://github.com/brotto/quantum_mega-sena_analitcs`
5. Branch: `main`

### 2. Configurar Variáveis de Ambiente

Na aba **"Environment Variables"**, adicione:

```
DB_HOST=nome-do-servico-postgres
DB_PORT=5432
DB_NAME=megasena
DB_USER=postgres
DB_PASSWORD=sua_senha_do_banco
OPENAI_API_KEY=sk-sua-chave-openai (opcional)
```

**⚠️ IMPORTANTE:** 
- `DB_HOST` deve ser o **nome do serviço** do seu PostgreSQL no Easypanel
- Geralmente algo como: `postgres-megasena` ou similar

### 3. Deploy

1. Easypanel detectará o **Dockerfile** automaticamente
2. Clique em **"Deploy"**
3. Aguarde o build (1-3 minutos)

### 4. Testar

Acesse a URL gerada pelo Easypanel (ex: `https://megasena-api-xxx.easypanel.host`):

- **Raiz:** `/` - Informações da API
- **Health Check:** `/health` - Verifica conexão com banco
- **Docs:** `/docs` - Documentação interativa automática (FastAPI)

## Endpoints Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Informações da API |
| `/health` | GET | Verifica saúde da API e banco |
| `/sorteios/todos` | GET | Retorna todos os sorteios |
| `/sorteios/ultimos/{n}` | GET | Retorna últimos N sorteios |
| `/sorteios/concurso/{numero}` | GET | Retorna sorteio específico |
| `/sorteios/json` | GET | Formato compatível com o projeto |
| `/estatisticas/frequencia` | GET | Frequência de cada número |

## Integração com n8n

### HTTP Request Node

```javascript
URL: https://sua-api.easypanel.host/sorteios/ultimos/10
Method: GET
```

### Exemplo de resposta:

```json
{
  "total": 10,
  "sorteios": [
    {
      "concurso": 2850,
      "data": "2024-12-22",
      "dezenas": [5, 12, 23, 34, 45, 56]
    }
  ]
}
```

## Troubleshooting

### Erro: "Erro ao conectar no banco de dados"

**Solução:**
1. Verifique se o `DB_HOST` está correto (nome do serviço PostgreSQL)
2. Verifique se o banco está rodando
3. Teste a conexão: acesse `/health` na API

### Erro: "Table 'sorteios_megasena' doesn't exist"

**Solução:**
1. Conecte no PostgreSQL via Easypanel
2. Execute o SQL de criação da tabela (ver acima)

### API não inicia

**Solução:**
1. Veja os logs no Easypanel (aba "Logs")
2. Verifique se todas as variáveis de ambiente estão configuradas
3. Confirme que o Dockerfile foi detectado

## Atualizar a API

Sempre que fizer alterações no código:

```bash
git add .
git commit -m "Descrição da alteração"
git push origin main
```

O Easypanel fará **deploy automático** das alterações!

## Estrutura da Tabela

Se você não tiver os dados ainda, pode importar do JSON existente ou configurar um workflow n8n para popular automaticamente.

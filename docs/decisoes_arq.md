# Decisões Arquiteturais

Este documento tem por objetivo registrar as principais tomadas de decisão feitas durante o projeto, bem como os responsáveis, os impactos e as justificativas.
---

## DevOps

### Decisão 
- **Descrição:**
- **Responsável:**
- **Alternativas consideradas:**
    - 
- **Decisão tomada:**
- **Principais impactos:**
- **Observações:** 

## Engenharia de Dados

### Decisão 
- **Descrição:** Escolha de parametros para a ML
- **Responsável:**
- **Alternativas consideradas:**
    - 
- **Decisão tomada:**
- **Principais impactos:**
- **Observações:** 

## Modelo Preditivo

### Decisão 1
- **Descrição:** Escolha do modelo de predição multi-step
- **Responsável:** Luís Filipe
- **Alternativas consideradas:**
    - ARIMA / Prophet
    - RNN / LSTM
    - LGBM / LightGBM
- **Decisão tomada:** Modelo LightGBM escolhido pela simplicidade, fácil manutenção, desempenho rápido e consistência.
- **Principais impactos:** Treino mais rápido, integração com pipeline, fácil manutenção e armazenamento dos modelos no GCS.
- **Observações:** 

### Decisão 2
- **Descrição:** Tamanho do contexto e Horizon
- **Responsável:** Luís Filipe
- **Alternativas consideradas:**
    - Contexto de 15, 30, 45, 60 e 90 dias
    - Horizon de 1, 3 e 7 dias
- **Decisão tomada:**
    - Contexto de 45 escolhido por dar ao modelo uma visão melhor das mudanças e associar com a sazonalidade, mas mantendo um custo menor.
    - Horizon de 7, que pode gerar melhores insights e inclui previsão do primeiro dia.
- **Principais impactos:** Captura tendências sazonais com mais precisão, gera predições mais completas.
- **Observações:** O aumento do horizon diminui a confiabilidade do modelo, mas a arquitetura compensa e a mantém num nível seguro (cerca de 75% a 80%).

### Decisão 3
- **Descrição:** Caracterização dos reservatórios
- **Responsável:** Luís Filipe
- **Alternativas consideradas:**
    - Indexação por id
    - Média global por reservatório
    - Média incremental por reservatório
    - Embedding com perfil de cadastro
- **Decisão tomada:** Média incremental, que reduz possíveis vazamentos de dados durante o treinamento mas consegue dar contexto do comportamento de cada reservatório
- **Principais impactos:** Maior especificidade na predição
- **Observações:** 

### Decisão 4
- **Descrição:** Armazenamento dos modelos
- **Responsável:** Luís Filipe
- **Alternativas consideradas:**
    - Armazenamento local
    - Google Cloud Storage
- **Decisão tomada:** GCS
- **Principais impactos:** Facilidade para integrar com o Cloud Run
- **Observações:** 

## Análise de Dados

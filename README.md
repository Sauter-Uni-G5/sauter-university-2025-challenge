# Sauter University - ML
## Integrantes
 [Alcielma L.](https://github.com/Alcielma) | [Allan J.](https://github.com/allanjose001) | [Ismael D.](https://github.com/ismael-ds-correia) | [Luis F. de Barros](https://github.com/luis-fil) | [Micaelle F.](https://github.com/micaelleffr)

## Sobre
Projeto da Sauter University: AI Specialists Programs. Este projeto consiste em treinar um modelo de Machine Learning usando LightGBM com implementações feitas utilizando todas as devidas ferramentas do Google Cloud Plataform.

## Como configurar
### API: Data_engineer.
- Utilizar Python versão 3.10 ou superior.
- Instalar as bibliotecas listadas no requiriments.txt.
- Comando para rodar a API: uvicorn main:app --reload
- URL padrão: http://127.0.0.1:8000
### Tags e Endpoints:
 - /api/hydro
 - /api/ear
 - /api/weather
 - /api/registry
 - /api/pipeline
### Exemplo de URL
http://127.0.0.1:8000/api/hydro?package_id=<ID_DO_PACKAGE>&start_date=2020-01-01&end_date=2021-12-31&page=1&page_size=100
Parametros:
- package_id (obrigatório): O ID do pacote de dados no ONS.
- ano (opcional): Ano específico para filtrar os dados.
- mes (opcional): Mês específico para filtrar os dados.
- nome_reservatorio (opcional): Nome do reservatório para filtrar.
- start_date (opcional): Data inicial no formato YYYY-MM-DD.
- end_date (opcional): Data final no formato YYYY-MM-DD.
- page (opcional): Número da página (padrão: 1).
- page_size (opcional): Quantidade de registros por página (padrão: 100).

### Saida padrão de requisição:
{
  "data": [
    {
      "reservatorio": "Reservatório Y",
      "energia_armazenada": 78.9,
      "data": "2020-01-01"
    },
    ...
  ],
  "page": 1,
  "page_size": 50,
  "total_pages": 20
}

##Decisões de arquitetura
###Engenharia de Dados
O objetivo do projeto era coletar dados de reservatórios pelo site da ONS e fazer toda a normalização e tratamentos necessários.
Primeiramente foi criado um endpoint que recebe uma data inicial e final e então faz o donwload temporario dos arquivos .parquet dos anos que foram solicitados, e então transforma estes
arquivos em um Json para ser enviado pelo endpoint. 

Nós optamos por escolher dois arquivos do sistema da ONS, o EAR(Energia Armazenada dos Reservatórios) e os dados hidrológicos de todos os reservatórios.
Os dados hidrológicos foram selecionados pois queriamos os dados de volume máximo consistido 

Os dados do Json que foram recebidos são recebidos pelos extractors que transforma a entrada em um Dataframe do pandas, onde os valores muito quebrados são tratados, os

## Tecnologias Usadas

### <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg" height="40" alt="java logo"/> [Python](https://www.python.org)
* Versão 3.8.10

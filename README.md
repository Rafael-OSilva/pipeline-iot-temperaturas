# Pipeline de Dados com IoT e Docker

Projeto acadêmico de processamento e análise de leituras de temperatura de dispositivos IoT, utilizando Python, PostgreSQL, Docker, SQL, Streamlit e Plotly.

## 1. Objetivo

Construir um pipeline de dados capaz de ler um dataset CSV de temperaturas, tratar e validar os registros, armazená-los em PostgreSQL executado em Docker e disponibilizar análises por meio de consultas SQL e um dashboard interativo.

## 2. Tecnologias

- **Python** — implementação do pipeline e da aplicação.
- **Pandas** — leitura, tratamento e análise dos dados.
- **PostgreSQL** — armazenamento relacional.
- **Docker Compose** — execução local do banco de dados.
- **SQLAlchemy / psycopg2** — conexão Python–PostgreSQL.
- **Streamlit** — aplicação web do dashboard.
- **Plotly** — gráficos interativos.
- **PyCharm** — ambiente de desenvolvimento.

## 3. Dataset

Dataset: **Temperature Readings: IoT Devices**, disponível no Kaggle:  
https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices

O arquivo utilizado durante o desenvolvimento foi `IOT-temp.csv`.

Colunas originais observadas:
- `id`
- `room_id/id`
- `noted_date`
- `temp`
- `out/in`

A análise inicial identificou 97.606 linhas, cinco colunas e nenhum valor ausente. A temperatura média observada foi aproximadamente 35,05, com mínimo 21 e máximo 51. A unidade de medida deve ser confirmada na documentação original do dataset antes de ser descrita como °C.

Após a remoção de uma linha duplicada completa, o pipeline produziu 97.605 registros para carga. A coluna `room_id/id` apresentou apenas o valor `Room Admin` na análise realizada; por isso, as análises do dashboard comparam `In` e `Out`, em vez de comparar ambientes diferentes.

## 4. Arquitetura e fluxo

1. O CSV é lido pelo Python/Pandas.
2. Os nomes das colunas são verificados.
3. A temperatura é convertida para valor numérico e `noted_date` é convertida para data/hora.
4. Registros com campos essenciais inválidos são descartados e duplicatas completas são removidas.
5. São derivadas as colunas `data_leitura` e `hora_leitura`.
6. Os dados tratados são inseridos na tabela `leituras_temperatura`.
7. As views SQL agregam os dados para análises.
8. O dashboard consulta a tabela e as views para exibir indicadores e gráficos.

## 5. Estrutura do projeto

```text
pipeline-iot-temperaturas/
├── data/
│   └── IOT-temp.csv                 # dataset local
├── src/
│   ├── analisar_csv.py              # análise exploratória inicial
│   ├── pipeline.py                  # tratamento e carga no PostgreSQL
│   └── dashboard.py                 # dashboard Streamlit + Plotly
├── sql/
│   ├── 01_criar_tabela.sql          # estrutura da tabela
│   └── 02_criar_views.sql           # três views analíticas
├── docker-compose.yml               # serviço PostgreSQL
├── .env.example                     # exemplo de configuração (recomendado)
├── .gitignore                       # arquivos não versionados (recomendado)
└── README.md
```

## 6. Pré-requisitos

- Python instalado.
- Docker Desktop instalado e em execução.
- Git, caso vá clonar o repositório.
- Dataset `IOT-temp.csv` colocado na pasta `data/`.

## 7. Instalação e execução local

### 7.1 Clonar o projeto

```bash
git clone (https://github.com/Rafael-OSilva/pipeline-iot-temperaturas)
cd pipeline-iot-temperaturas
```

### 7.2 Criar e ativar o ambiente virtual

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 7.3 Instalar dependências

Crie ou confira `requirements.txt` com as dependências utilizadas:

```text
pandas
sqlalchemy
psycopg2-binary
streamlit
plotly
python-dotenv
```

Depois execute:

```powershell
python -m pip install -r requirements.txt
```

### 7.4 Iniciar o PostgreSQL

Na pasta raiz do projeto:

```powershell
docker compose up -d
docker compose ps
```

Aguarde o serviço aparecer como `healthy`.

### 7.5 Criar tabela e views

Se os arquivos SQL estiverem salvos conforme a estrutura:

```powershell
Get-Content .\sql\01_criar_tabela.sql | docker compose exec -T postgres psql -U iot_user -d iot_temperaturas
Get-Content .\sql\02_criar_views.sql | docker compose exec -T postgres psql -U iot_user -d iot_temperaturas
```

Verificar as views:

```powershell
docker compose exec postgres psql -U iot_user -d iot_temperaturas -c "\dv"
```

### 7.6 Executar o pipeline

```powershell
python src/pipeline.py
```

O pipeline atual limpa a tabela antes de carregar os dados. Use somente no banco local de desenvolvimento, pois uma nova execução substitui os registros já existentes.

### 7.7 Conferir a quantidade de registros

```powershell
docker compose exec postgres psql -U iot_user -d iot_temperaturas -c "SELECT COUNT(*) FROM leituras_temperatura;"
```

No processamento realizado durante o desenvolvimento, o resultado esperado foi `97605`.

### 7.8 Executar o dashboard

Com o banco em execução:

```powershell
python -m streamlit run src/dashboard.py
```

Abra o endereço local indicado pelo Streamlit, normalmente `http://localhost:8501`.

## 8. Modelo de dados

A tabela `leituras_temperatura` contém:
- `id_registro`: chave primária gerada pelo PostgreSQL.
- `id_original`: identificador original do CSV.
- `room_id`: valor original da coluna `room_id/id`.
- `noted_date`: data e hora da leitura.
- `temp`: temperatura registrada.
- `local_leitura`: valor original de `out/in` (`In` ou `Out`).
- `data_leitura`: data derivada da leitura.
- `hora_leitura`: hora do dia derivada da leitura.

## 9. Views SQL

### `vw_temperatura_por_local`
Agrupa por `local_leitura` e retorna total de leituras, média, mínimo e máximo.

### `vw_leituras_por_hora`
Agrupa por hora do dia e retorna total de leituras e temperatura média.

### `vw_temperaturas_por_dia`
Agrupa por data e retorna total de leituras, média, mínima e máxima.

## 10. Dashboard

O dashboard apresenta:
- total de leituras;
- temperatura média, mínima e máxima;
- distribuição de leituras entre `In` e `Out`;
- temperatura média por hora;
- evolução diária das temperaturas mínima, média e máxima;
- tabelas com os resultados das views SQL.

## 11. Validação realizada

Durante o desenvolvimento:
- o script de análise exploratória foi executado com sucesso;
- o tratamento do CSV foi concluído sem erro;
- o PostgreSQL foi iniciado via Docker Compose e chegou ao estado `healthy`;
- a tabela foi criada;
- foram confirmadas 97.605 linhas na tabela;
- as três views foram criadas e listadas pelo PostgreSQL;
- o dashboard abriu no navegador e apresentou indicadores e gráficos.

## 12. Limitações e cuidados

- A unidade da temperatura deve ser confirmada na fonte do dataset.
- `room_id/id` apresentou apenas `Room Admin` no arquivo analisado.
- A classificação `In`/`Out` é mantida conforme o dado original; seu significado deve ser interpretado conforme a documentação do dataset.
- O pipeline atual limpa a tabela antes da carga, portanto não deve ser usado indiscriminadamente em bancos com dados importantes.
- Para publicar o projeto, não envie senhas reais, ambiente virtual ou dados que não possam ser redistribuídos. Configure credenciais por variáveis de ambiente em uma versão posterior.
- O arquivo CSV pode ser grande ou sujeito a condições de licença; se não for apropriado incluí-lo no GitHub, explique no README como baixá-lo e onde colocá-lo.

## 13. Autoria

- **Aluno:** Rafael Oliveira da Silva
- **Curso:** Analise e desenvolvimento de sistemas
- **Disciplina:** Disruptive Architectures: IoT, Big Data e IA
- **Instituição:** Unifecaf
- **Repositório:** https://github.com/Rafael-OSilva/pipeline-iot-temperaturas


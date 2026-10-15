
from pathlib import Path

import pandas as pd

# Localiza a pasta principal do projeto
PASTA_PROJETO = Path(__file__).resolve().parent.parent

# Caminho do arquivo CSV
ARQUIVO_CSV = PASTA_PROJETO / "data" / "IOT-temp.csv"


def analisar_csv():
    print("=" * 60)
    print("ANÁLISE INICIAL DOS DADOS DE TEMPERATURA IoT")
    print("=" * 60)

    # Verifica se o arquivo existe
    if not ARQUIVO_CSV.exists():
        print(f"Arquivo não encontrado: {ARQUIVO_CSV}")
        print("Confira se o CSV está dentro da pasta data.")
        return

    # Lê o arquivo CSV
    df = pd.read_csv(ARQUIVO_CSV)

    print("\n1. Dimensões do arquivo")
    print(f"Quantidade de linhas: {df.shape[0]}")
    print(f"Quantidade de colunas: {df.shape[1]}")

    print("\n2. Nomes das colunas")
    print(df.columns.tolist())

    print("\n3. Primeiros cinco registros")
    print(df.head().to_string(index=False))

    print("\n4. Tipos de dados e valores preenchidos")
    df.info()

    print("\n5. Valores ausentes por coluna")
    print(df.isnull().sum())

    print("\n6. Resumo estatístico")
    print(df.describe(include="all").to_string())


if __name__ == "__main__":
    analisar_csv()

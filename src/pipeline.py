
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# Caminhos do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "IOT-temp.csv"

# Configuração do PostgreSQL local no Docker
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username="iot_user",
    password="iot_dev_password",
    host="localhost",
    port=5432,
    database="iot_temperaturas",
)

COLUNAS_OBRIGATORIAS = [
    "id",
    "room_id/id",
    "noted_date",
    "temp",
    "out/in",
]


def carregar_dados():
    """Carrega o arquivo CSV original."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo CSV não encontrado: {CSV_PATH}"
        )

    df = pd.read_csv(CSV_PATH)

    print(f"Arquivo carregado: {CSV_PATH.name}")
    print(f"Registros originais: {len(df)}")

    return df


def tratar_dados(df):
    """Limpa e prepara os dados para o banco."""

    df = df.copy()
    df.columns = df.columns.str.strip()

    faltantes = [
        coluna
        for coluna in COLUNAS_OBRIGATORIAS
        if coluna not in df.columns
    ]

    if faltantes:
        raise ValueError(
            f"Colunas ausentes no CSV: {faltantes}"
        )

    df["temp"] = pd.to_numeric(
        df["temp"], errors="coerce"
    )

    df["noted_date"] = pd.to_datetime(
        df["noted_date"],
        format="%d-%m-%Y %H:%M",
        errors="coerce",
    )

    for coluna in ["id", "room_id/id", "out/in"]:
        df[coluna] = df[coluna].astype("string").str.strip()

    df = df.dropna(
        subset=[
            "id",
            "room_id/id",
            "noted_date",
            "temp",
            "out/in",
        ]
    )

    df = df.drop_duplicates().copy()

    # Nomes correspondentes às colunas do PostgreSQL
    df = df.rename(
        columns={
            "id": "id_original",
            "room_id/id": "room_id",
            "out/in": "local_leitura",
        }
    )

    df["data_leitura"] = df["noted_date"].dt.date
    df["hora_leitura"] = df["noted_date"].dt.hour

    # Mantém somente as colunas necessárias
    df = df[
        [
            "id_original",
            "room_id",
            "noted_date",
            "temp",
            "local_leitura",
            "data_leitura",
            "hora_leitura",
        ]
    ]

    print(f"Registros após tratamento: {len(df)}")

    return df


def carregar_no_postgres(df):
    """Insere os registros tratados no PostgreSQL."""

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )

    try:
        # Confirma a conexão antes de importar
        with engine.connect() as conexao:
            conexao.execute(text("SELECT 1"))

        print("Conexão com PostgreSQL estabelecida!")

        # Substitui dados anteriores para evitar duplicação
        # em novas execuções deste pipeline.
        with engine.begin() as conexao:
            conexao.execute(
                text("TRUNCATE TABLE leituras_temperatura "
                     "RESTART IDENTITY")
            )

        df.to_sql(
            name="leituras_temperatura",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=5000,
            method="multi",
        )

        with engine.connect() as conexao:
            total = conexao.execute(
                text("SELECT COUNT(*) FROM leituras_temperatura")
            ).scalar_one()

        print(f"Registros gravados no PostgreSQL: {total}")

        if total != len(df):
            raise RuntimeError(
                f"Esperados {len(df)} registros, "
                f"mas foram encontrados {total}."
            )

    finally:
        engine.dispose()


def main():
    df = carregar_dados()
    df_tratado = tratar_dados(df)

    print("\nIniciando importação para PostgreSQL...")
    carregar_no_postgres(df_tratado)

    print("\nPipeline concluído com sucesso!")


if __name__ == "__main__":
    main()

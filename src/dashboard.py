
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# Configuração da página
st.set_page_config(
    page_title="Flow de Temperaturas IoT",
    page_icon="🌡️",
    layout="wide",
)

# Conexão com PostgreSQL
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username="iot_user",
    password="iot_dev_password",
    host="localhost",
    port=5432,
    database="iot_temperaturas",
)

@st.cache_resource
def conectar_banco():
    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )


@st.cache_data(ttl=60)
def consultar_sql(sql):
    return pd.read_sql_query(sql, conectar_banco())


st.title("🌡️ Dashboard de Temperaturas IoT")
st.caption(
    "Análise das leituras de temperatura armazenadas no PostgreSQL"
)

try:
    # Indicadores gerais
    resumo = consultar_sql("""
        SELECT
            COUNT(*) AS total,
            ROUND(AVG(temp)::numeric, 2) AS media,
            MIN(temp) AS minima,
            MAX(temp) AS maxima
        FROM leituras_temperatura
    """)

    por_local = consultar_sql("""
        SELECT *
        FROM vw_temperatura_por_local
        ORDER BY local_leitura
    """)

    por_hora = consultar_sql("""
        SELECT *
        FROM vw_leituras_por_hora
        ORDER BY hora_leitura
    """)

    por_dia = consultar_sql("""
        SELECT *
        FROM vw_temperaturas_por_dia
        ORDER BY data_leitura
    """)

    # Cartões de indicadores
    total = int(resumo.loc[0, "total"])
    media = float(resumo.loc[0, "media"])
    minima = int(resumo.loc[0, "minima"])
    maxima = int(resumo.loc[0, "maxima"])

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total de leituras", f"{total:,}".replace(",", "."))
    c2.metric("Temperatura média", f"{media:.2f}")
    c3.metric("Temperatura mínima", minima)
    c4.metric("Temperatura máxima", maxima)

    st.divider()

    # Gráfico 1: leituras por classificação
    st.subheader("Leituras por classificação")

    fig_local = px.bar(
        por_local,
        x="local_leitura",
        y="total_leituras",
        color="local_leitura",
        text="total_leituras",
        labels={
            "local_leitura": "Classificação",
            "total_leituras": "Quantidade de leituras",
        },
        title="Distribuição entre In e Out",
    )
    st.plotly_chart(fig_local, use_container_width=True)

    # Gráfico 2: temperatura média por hora
    st.subheader("Temperatura média por hora")

    fig_hora = px.line(
        por_hora,
        x="hora_leitura",
        y="temperatura_media",
        markers=True,
        labels={
            "hora_leitura": "Hora do dia",
            "temperatura_media": "Temperatura média",
        },
        title="Temperatura média ao longo das 24 horas",
    )
    fig_hora.update_xaxes(dtick=1)
    st.plotly_chart(fig_hora, use_container_width=True)

    # Gráfico 3: evolução diária
    st.subheader("Evolução diária das temperaturas")

    fig_dia = px.line(
        por_dia,
        x="data_leitura",
        y=["temperatura_minima", "temperatura_media",
           "temperatura_maxima"],
        markers=True,
        labels={
            "data_leitura": "Data",
            "value": "Temperatura",
            "variable": "Métrica",
        },
        title="Temperaturas mínima, média e máxima por dia",
    )
    st.plotly_chart(fig_dia, use_container_width=True)

    # Tabela de dados
    with st.expander("Consultar dados das views SQL"):
        st.markdown("**Resumo por classificação**")
        st.dataframe(por_local, use_container_width=True)

        st.markdown("**Resumo por hora**")
        st.dataframe(por_hora, use_container_width=True)

        st.markdown("**Resumo por dia**")
        st.dataframe(por_dia, use_container_width=True)

except Exception as erro:
    st.error(
        "Não foi possível consultar o banco de dados. "
        "Confirme se o Docker está em execução e se as "
        "tabelas e views foram criadas."
    )
    st.exception(erro)

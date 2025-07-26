import streamlit as st
import pandas as pd
from io import BytesIO
import os

st.set_page_config(page_title="Tabela de Jogos 2025", layout="wide")

st.title("🏀 Editor de Tabela de Jogos - Festival 2025")

# Leitura direta da planilha local
a_uploaded_file = "tabela_festival_2025.xlsx"
df = pd.read_excel(a_uploaded_file, sheet_name="Sheet1")

st.subheader("🖊️ Editar Resultados dos Jogos")
edit_columns = ["Resultado_Time1", "Resultado_Time2"]
edited_df = st.data_editor(
    df,
    num_rows="fixed",
    disabled=[col for col in df.columns if col not in edit_columns],
    key="editor"
)

# Detecção de mudanças e salvamento automático (sem rerun)
if edited_df[edit_columns].astype(str).ne(df[edit_columns].astype(str)).any(axis=None):
    with pd.ExcelWriter(a_uploaded_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        edited_df.to_excel(writer, index=False, sheet_name="Sheet1")
    st.info("✅ Alterações salvas automaticamente.")

# Botão para gerar classificação
if st.button("Atualizar Classificação e Ranking"):
    # Filtrar apenas jogos com resultados preenchidos
    jogos_validos = edited_df.dropna(subset=["Resultado_Time1", "Resultado_Time2"])

    # Exibir alerta se houver jogos incompletos
    jogos_pendentes = len(edited_df) - len(jogos_validos)
    if jogos_pendentes > 0:
        st.warning(f"⚠️ Existem {jogos_pendentes} jogos ainda sem resultado preenchido.")

    # Cálculo de classificação
    todos_times = pd.concat([
        edited_df[["Time1"]].rename(columns={"Time1": "Time"}),
        edited_df[["Time2"]].rename(columns={"Time2": "Time"})
    ]).drop_duplicates().reset_index(drop=True)

    times = pd.concat([
        jogos_validos[["Time1", "Resultado_Time1", "Resultado_Time2"]].rename(
            columns={"Time1": "Time", "Resultado_Time1": "Gols_Pro", "Resultado_Time2": "Gols_Contra"}),
        jogos_validos[["Time2", "Resultado_Time2", "Resultado_Time1"]].rename(
            columns={"Time2": "Time", "Resultado_Time2": "Gols_Pro", "Resultado_Time1": "Gols_Contra"})
    ])

    times["Pontos"] = times.apply(lambda row: 3 if row.Gols_Pro > row.Gols_Contra else 1 if row.Gols_Pro == row.Gols_Contra else 0, axis=1)
    times["Vitoria"] = times["Gols_Pro"] > times["Gols_Contra"]
    times["Empate"] = times["Gols_Pro"] == times["Gols_Contra"]
    times["Derrota"] = times["Gols_Pro"] < times["Gols_Contra"]

    tabela = times.groupby("Time").agg(
        Jogos=("Time", "count"),
        Pontos=("Pontos", "sum"),
        Vitorias=("Vitoria", "sum"),
        Empates=("Empate", "sum"),
        Derrotas=("Derrota", "sum"),
        Gols_Pro=("Gols_Pro", "sum"),
        Gols_Contra=("Gols_Contra", "sum")
    ).reindex(todos_times["Time"]).fillna(0).reset_index()

    tabela["Saldo"] = tabela["Gols_Pro"] - tabela["Gols_Contra"]
    tabela = tabela.sort_values(by=["Pontos", "Saldo", "Gols_Pro"], ascending=False).reset_index(drop=True)
    tabela.index += 1  # Começar índice com 1

    st.subheader("📈 Classificação Geral")
    st.dataframe(tabela, use_container_width=True)

    # Ranking dos goleiros menos vazados, considerando todos os goleiros mesmo sem jogos
    todos_goleiros = pd.concat([
        edited_df[["Goleiro_Time1"]].rename(columns={"Goleiro_Time1": "Goleiro"}),
        edited_df[["Goleiro_Time2"]].rename(columns={"Goleiro_Time2": "Goleiro"})
    ]).drop_duplicates().reset_index(drop=True)

    goleiros_t1 = jogos_validos[["Goleiro_Time1", "Resultado_Time2"]].rename(
        columns={"Goleiro_Time1": "Goleiro", "Resultado_Time2": "Gols_Sofridos"})
    goleiros_t2 = jogos_validos[["Goleiro_Time2", "Resultado_Time1"]].rename(
        columns={"Goleiro_Time2": "Goleiro", "Resultado_Time1": "Gols_Sofridos"})
    goleiros = pd.concat([goleiros_t1, goleiros_t2])

    ranking = goleiros.groupby("Goleiro").agg(
        Jogos=("Goleiro", "count"),
        Gols_Sofridos=("Gols_Sofridos", "sum")
    ).reindex(todos_goleiros["Goleiro"]).fillna(0)
    ranking["Media"] = ranking.apply(lambda x: round(x.Gols_Sofridos / x.Jogos, 2) if x.Jogos > 0 else 0, axis=1)
    ranking = ranking.sort_values(by="Media").reset_index()

    st.subheader("🏆 Ranking dos Goleiros - Menos Vazados")
    st.dataframe(ranking, use_container_width=True)

    # Salvar classificação e ranking também na planilha
    with pd.ExcelWriter(a_uploaded_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        edited_df.to_excel(writer, index=False, sheet_name="Sheet1")
        tabela.to_excel(writer, sheet_name="Classificacao", index=False)
        ranking.to_excel(writer, sheet_name="RankingGoleiros", index=False)

    st.success("✅ Planilha atualizada com sucesso!")

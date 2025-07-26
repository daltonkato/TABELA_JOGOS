import pandas as pd
import streamlit as st


st.title('Festival Society SCCP - 2025')
st.write("---")


# Leitura dos dados da planilha Excel
arquivo_excel = 'tabela_festival_2025.xlsx'  # Substitua pelo caminho do seu arquivo
df = pd.read_excel(arquivo_excel)




def section_1():
    # Exibição dos resultados dos jogos
    print("Resultados dos Jogos:")
    print(df)
    df.index += 1

    st.write("Tabela de Jogos")
    st.dataframe(df)

# Inicialização de dicionários para guardar as estatísticas dos times e goleiros
estatisticas_times = {}
estatisticas_goleiros = {}

# Função para atualizar as estatísticas dos times
def atualizar_estatisticas_time(time, gols_pro, gols_contra, vitoria, empate, derrota, num_jogos):
    if time not in estatisticas_times:
        estatisticas_times[time] = {
            'PTs': 0,
            'VIT': 0,
            'E': 0,
            'D': 0,
            'GP': 0,
            'GC': 0,
            'SG': 0,
            'PJ': 0
        }
    
    estatisticas_times[time]['PTs'] += 3 * vitoria + 1 * empate
    estatisticas_times[time]['VIT'] += vitoria
    estatisticas_times[time]['E'] += empate
    estatisticas_times[time]['D'] += derrota
    estatisticas_times[time]['GP'] += gols_pro
    estatisticas_times[time]['GC'] += gols_contra
    estatisticas_times[time]['SG'] = estatisticas_times[time]['GP'] - estatisticas_times[time]['GC']
    estatisticas_times[time]['PJ'] += num_jogos

# Função para atualizar as estatísticas dos goleiros
def atualizar_estatisticas_goleiro(goleiro, gols_contra, PTs, vitoria, empate, num_jogos):
    if goleiro not in estatisticas_goleiros:
        estatisticas_goleiros[goleiro] = {
            'Gols Sofridos': 0,
            'PTs': 0,
            'VIT': 0,
            'E': 0, 
            'PJ': 0
        }
    
    estatisticas_goleiros[goleiro]['Gols Sofridos'] += gols_contra
    estatisticas_goleiros[goleiro]['PTs'] += PTs
    estatisticas_goleiros[goleiro]['VIT'] += vitoria
    estatisticas_goleiros[goleiro]['E'] += empate
    estatisticas_goleiros[goleiro]['PJ'] += num_jogos

# Processamento dos dados para calcular os resultados
for _, row in df.iterrows():
    time1 = row['Time1']
    time2 = row['Time2']
    resultado_time1 = row['Resultado_Time1']
    resultado_time2 = row['Resultado_Time2']
    goleiro_time1 = row['Goleiro_Time1']
    goleiro_time2 = row['Goleiro_Time2']
    
    # Verifica se os resultados não são None
    if pd.notna(resultado_time1) and pd.notna(resultado_time2):
        if resultado_time1 > resultado_time2:
            # Time1 vence
            atualizar_estatisticas_time(time1, resultado_time1, resultado_time2, 1, 0, 0, 1)
            atualizar_estatisticas_time(time2, resultado_time2, resultado_time1, 0, 0, 1, 1)
            atualizar_estatisticas_goleiro(goleiro_time1, resultado_time2, 3, 1, 0, 1)
            atualizar_estatisticas_goleiro(goleiro_time2, resultado_time1, 0, 0, 0, 1)
        elif resultado_time1 < resultado_time2:
            # Time2 vence
            atualizar_estatisticas_time(time1, resultado_time1, resultado_time2, 0, 0, 1, 1)
            atualizar_estatisticas_time(time2, resultado_time2, resultado_time1, 1, 0, 0, 1)
            atualizar_estatisticas_goleiro(goleiro_time1, resultado_time2, 0, 0, 0, 1)
            atualizar_estatisticas_goleiro(goleiro_time2, resultado_time1, 3, 1, 0, 1)
        else:
            # Empate
            atualizar_estatisticas_time(time1, resultado_time1, resultado_time2, 0, 1, 0, 1)
            atualizar_estatisticas_time(time2, resultado_time2, resultado_time1, 0, 1, 0, 1)
            atualizar_estatisticas_goleiro(goleiro_time1, resultado_time2, 1, 0, 1, 1)
            atualizar_estatisticas_goleiro(goleiro_time2, resultado_time1, 1, 0, 1, 1)
    else:
        atualizar_estatisticas_time(time1, 0, 0, 0, 0, 0, 0)
        atualizar_estatisticas_time(time2, 0, 0, 0, 0, 0, 0)
        atualizar_estatisticas_goleiro(goleiro_time1, 0, 0, 0, 0, 0)
        atualizar_estatisticas_goleiro(goleiro_time2, 0, 0, 0, 0, 0)



def section_2():
    # Criação de um DataFrame a partir das estatísticas dos times
    tabela_classificacao_times = pd.DataFrame.from_dict(estatisticas_times, orient='index')

    # Ordenação da tabela de classificação dos times
    tabela_classificacao_times = tabela_classificacao_times.sort_values(
        by=['PTs', 'VIT', 'SG', 'GP', 'GC'],
        ascending=[False, False, False, False, True]
    )

    # Resetando o índice e adicionando a coluna de ordem
    tabela_classificacao_times = tabela_classificacao_times.reset_index().rename(columns={'index': 'Time'})
    tabela_classificacao_times.index += 1  # Ajusta o índice do DataFrame para começar em 1
    #tabela_classificacao_times['Ordem'] = tabela_classificacao_times.index

    # Exibição da tabela de classificação dos times
    print("\nTabela de Classificação dos Times:")
    print(tabela_classificacao_times)
    st.write("Classificação Geral")

    nova_ordem = ['Time', 'PTs','PJ','VIT','SG', 'D','E','GP', 'GC']

    print(tabela_classificacao_times[nova_ordem])   


    st.dataframe(tabela_classificacao_times[nova_ordem])


def section_3():
    # Criação de um DataFrame a partir das estatísticas dos goleiros
    tabela_classificacao_goleiros = pd.DataFrame.from_dict(estatisticas_goleiros, orient='index')

    # Ordenação da tabela de classificação dos goleiros
    tabela_classificacao_goleiros = tabela_classificacao_goleiros.sort_values(
        by=['Gols Sofridos', 'PTs', 'VIT', 'E'],
        ascending=[True, False, False, False]
    )

    # Resetando o índice e adicionando a coluna de ordem
    tabela_classificacao_goleiros = tabela_classificacao_goleiros.reset_index().rename(columns={'index': 'Goleiro'})
    tabela_classificacao_goleiros.index += 1  # Ajusta o índice do DataFrame para começar em 1
    #tabela_classificacao_goleiros['Ordem'] = tabela_classificacao_goleiros.index
    # Exibição da tabela de classificação dos goleiros
    print("\nTabela de Classificação dos Goleiros:")
    print(tabela_classificacao_goleiros)
    st.write("Classificação dos Goleiros")
    st.dataframe(tabela_classificacao_goleiros)

# Barra lateral com os botões
st.sidebar.title("Menu de Navegação")
if st.sidebar.button("Tabela Jogos"):
    section_1()
if st.sidebar.button("Classificação Times"):
    section_2()
if st.sidebar.button("Classificação Goleiros"):
    section_3()


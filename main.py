#importações das bibliotecas
import pandas as pd
import requests
from scipy.stats import poisson
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, jsonify, request, send_file
from scipy.stats import poisson
from flask_cors import CORS
import io

seriaA2024 = requests.get('https://pt.wikipedia.org/wiki/Campeonato_Brasileiro_de_Futebol_de_2024_-_S%C3%A9rie_A')

# Informações do campeonato de 2024
tabelas2024 = pd.read_html(seriaA2024.text)
tabela_classificação2024 = tabelas2024[6]
tabela_jogos2024 = tabelas2024[7]

#criando uma lista com os nomes dos times
nomes_times_2024 = list(tabela_jogos2024["Casa \ Fora"])
sigla_times_2024 = list(tabela_jogos2024.columns)
sigla_times_2024.pop(0)
apelidos_times_2024 = dict(zip(sigla_times_2024, nomes_times_2024))

# Ajustar a tabela de jogos
tabela_jogos2024_ajustada = tabela_jogos2024.set_index("Casa \ Fora")

# Desempilhar a tabela
tabela_jogos2024_ajustada = tabela_jogos2024_ajustada.unstack().reset_index()

# Renomear as colunas
tabela_jogos2024_ajustada = tabela_jogos2024_ajustada.rename(columns={"level_0": "Fora", "Casa \ Fora": "Casa", 0: "Placar"})

# Função para ajustar o nome dos times
def ajustar_apelido(linha, apelido):
    time = linha["Fora"]
    return apelido[time]

# Ajustar o nome dos times aplicando a função
tabela_jogos2024_ajustada["Fora"] = tabela_jogos2024_ajustada.apply(ajustar_apelido, axis=1, args=(apelidos_times_2024,))
# Remover jogos entre o mesmo time
tabela_jogos2024_ajustada = tabela_jogos2024_ajustada[tabela_jogos2024_ajustada["Fora"] != tabela_jogos2024_ajustada["Casa"]]

tabela_jogos2024_ajustada["Placar"] = tabela_jogos2024_ajustada["Placar"].fillna("A jogar")

jogos_realizados = tabela_jogos2024_ajustada[tabela_jogos2024_ajustada["Placar"].str.contains("–")]
jogos_faltantes = tabela_jogos2024_ajustada[~tabela_jogos2024_ajustada["Placar"].str.contains("–")]
jogos_faltantes = jogos_faltantes.drop(columns=["Placar"])

# Separando a coluna Placar em gols_casa e gols_fora
jogos_realizados["gols_casa"] = jogos_realizados["Placar"].str.split("–").str[0].astype(int)
jogos_realizados["gols_fora"] = jogos_realizados["Placar"].str.split("–").str[1].astype(int)
jogos_realizados = jogos_realizados.drop(columns=["Placar"])

seriaA2023 = requests.get('https://pt.wikipedia.org/wiki/Campeonato_Brasileiro_de_Futebol_de_2023_-_S%C3%A9rie_A')

tabelas2023 = pd.read_html(seriaA2023.text)
tabela_jogos = tabelas2023[6]

nomes_times = list(tabela_jogos["Casa \ Fora"])
sigla_times = list(tabela_jogos.columns)
sigla_times.pop(0)

apelidos_times = dict(zip(sigla_times, nomes_times))

tabela_jogos_ajustada = tabela_jogos.set_index("Casa \ Fora")
tabela_jogos_ajustada = tabela_jogos_ajustada.unstack().reset_index()
tabela_jogos_ajustada = tabela_jogos_ajustada.rename(columns={"level_0": "Fora", "Casa \ Fora": "Casa", 0: "Placar"})

tabela_jogos_ajustada["Fora"] = tabela_jogos_ajustada.apply(ajustar_apelido, axis=1, args=(apelidos_times,))
tabela_jogos_ajustada = tabela_jogos_ajustada[tabela_jogos_ajustada["Casa"] != tabela_jogos_ajustada["Fora"]]

tabela_jogos_ajustada["gols_casa"] = tabela_jogos_ajustada["Placar"].str.split("–").str[0].astype(int)
tabela_jogos_ajustada["gols_fora"] = tabela_jogos_ajustada["Placar"].str.split("–").str[1].astype(int)
tabela_jogos_ajustada = tabela_jogos_ajustada.drop(columns=["Placar"])  

tabela_jogos_total = pd.concat([tabela_jogos_ajustada, jogos_realizados], ignore_index=True)
media_gols_casa = tabela_jogos_total.groupby("Casa").mean(numeric_only=True)
media_gols_casa = media_gols_casa.rename(columns={"gols_casa": "gols feitos_casa", "gols_fora": "gols sofridos_casa"})
media_gols_fora = tabela_jogos_total.groupby("Fora").mean(numeric_only=True)
media_gols_fora = media_gols_fora.rename(columns={"gols_casa": "gols sofridos_fora", "gols_fora": "gols feitos_fora"})

media_gols_casa = media_gols_casa.drop(index=["Santos", "Goiás", "Coritiba", "América Mineiro"])
media_gols_fora = media_gols_fora.drop(index=["Santos", "Goiás", "Coritiba", "América Mineiro"])

tabela_estatistica = media_gols_casa.merge(media_gols_fora, left_index=True, right_index=True)
tabela_estatistica = tabela_estatistica.reset_index()
tabela_estatistica = tabela_estatistica.rename(columns={"Casa": "Time"})


def calcular_pts_esperada(linha):
    # Disitribuição de Poisson - Eventos independentes
    time_casa = linha["Casa"]
    time_fora = linha["Fora"]


    # Media esperada de gols que o time da casa tem X contra o time fora de casa
    lambda_casa = tabela_estatistica.loc[tabela_estatistica["Time"] == time_casa, "gols feitos_casa"].iloc[0] * tabela_estatistica.loc[tabela_estatistica["Time"] == time_fora, "gols sofridos_fora"].iloc[0]

    # Media esperada de gols que o time fora de casa tem X contra o time da casa
    lambda_fora = tabela_estatistica.loc[tabela_estatistica["Time"] == time_fora, "gols feitos_fora"].iloc[0] * tabela_estatistica.loc[tabela_estatistica["Time"] == time_casa, "gols sofridos_casa"].iloc[0]


    pv_casa = 0
    p_empate = 0
    pv_fora = 0

    # Considerando fazer gols eventos independentes
    for gols_casa in range(0, 7):
        for gols_fora in range(0, 7):
            prob_resultado = poisson.pmf(gols_casa, lambda_casa) * poisson.pmf(gols_fora, lambda_fora)
            if gols_casa == gols_fora:
                p_empate += prob_resultado
            elif gols_casa > gols_fora:
                pv_casa += prob_resultado
            else:
                pv_fora += prob_resultado

    v_esperado_casa = pv_casa * 3 + p_empate
    v_esperado_fora = pv_fora * 3 + p_empate

    linha["pontos_casa"] = v_esperado_casa
    linha["pontos_fora"] = v_esperado_fora

    return linha

def gerar_heatMap(time_casa, time_fora):

    # Disitribuição de Poisson - Eventos independentes

    # Media esperada de gols que o time da casa tem X contra o time fora de casa
    lambda_casa = tabela_estatistica.loc[tabela_estatistica["Time"] == time_casa, "gols feitos_casa"].iloc[0] * tabela_estatistica.loc[tabela_estatistica["Time"] == time_fora, "gols sofridos_fora"].iloc[0]

    # Media esperada de gols que o time fora de casa tem X contra o time da casa
    lambda_fora = tabela_estatistica.loc[tabela_estatistica["Time"] == time_fora, "gols feitos_fora"].iloc[0] * tabela_estatistica.loc[tabela_estatistica["Time"] == time_casa, "gols sofridos_casa"].iloc[0]

    plt.figure(figsize=(10, 6))
    tabela_calculo = pd.DataFrame()

    # Considerando fazer gols eventos independentes
    for gols_casa in range(0, 7):
        for gols_fora in range(0, 7):
            prob_resultado = poisson.pmf(gols_casa, lambda_casa) * poisson.pmf(gols_fora, lambda_fora)
            tabela_calculo.loc[gols_casa, gols_fora] = prob_resultado

    sns.heatmap(tabela_calculo, annot=True, cmap="coolwarm")
    plt.title(f"{time_casa} x {time_fora}")
    plt.xlabel(f"Gols {time_fora}")
    plt.ylabel(f"Gols {time_casa}")

    heatMap = plt.gcf()
    return heatMap

tabela_jogos_faltantes = jogos_faltantes.apply(calcular_pts_esperada, axis=1)
tabela_classificação_atualizada = tabela_classificação2024[["Equipevde", "Pts"]]
tabela_classificação_atualizada["Pts"] = tabela_classificação_atualizada["Pts"].astype(int)

pts_casa = tabela_jogos_faltantes.groupby("Casa").sum()[["pontos_casa"]]
pts_fora = tabela_jogos_faltantes.groupby("Fora").sum()[["pontos_fora"]]

def atualizar_pts (linha):
    time = linha["Equipevde"]
    pontuacao = int(linha["Pts"]) + float(pts_casa.loc[time, "pontos_casa"]) + float(pts_fora.loc[time, "pontos_fora"])

    return pontuacao

tabela_classificação_atualizada["Pts"] = tabela_classificação_atualizada.apply(atualizar_pts, axis=1)
# Renomear a coluna
tabela_classificação_atualizada = tabela_classificação_atualizada.rename(columns={"Equipevde": "Time", "Pts": "Pontos"})
tabela_classificação_atualizada = tabela_classificação_atualizada.sort_values(by="Pontos", ascending=False).reset_index(drop=True)
tabela_classificação_atualizada.index = tabela_classificação_atualizada.index + 1

app = Flask(__name__)

plt.switch_backend('agg')
CORS(app)
@app.route('/', methods=['GET'])
def classificacao():
    return jsonify(tabela_classificação_atualizada.to_dict(orient="records"))

@app.route('/heatmap', methods=['POST'])
def heatmap():
    data = request.get_json()
    time_casa = data["time_casa"]
    time_fora = data["time_fora"]

    if not time_casa or not time_fora:
        return jsonify({"erro": "Os times não foram informados"}), 400
    
    heatMap = gerar_heatMap(time_casa, time_fora)
    buf = io.BytesIO()
    heatMap.savefig(buf, format='png')
    buf.seek(0)

    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(host="0.0.0.0")


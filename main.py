import numpy as np
import pandas as pd
import math
import streamlit as st

def regressao(x, y):
    n = len(x)
    sx, sy, sx2, sxy = sum(x), sum(y), sum(x ** 2), sum(x * y)
    a0 = (sx2 * sy - sxy * sx) / (n * sx2 - sx ** 2)
    a1 = (n * sxy - sx * sy) / (n * sx2 - sx ** 2)
    return a0, a1


# Carregar os dados do arquivo CSV
full = pd.read_csv("data_teams.csv")

st.sidebar.header('Menu')
paginas = ['Previsão Brasileirão Série A', 'Tabelas']
pagina = st.sidebar.radio('Selecione a página', paginas)

if pagina == 'Previsão Brasileirão Série A':
    st.markdown("<h2 style='text-align: center; color: #FFBE0B; font-size: 32px;'>Brasileirão Série A 2024 🏆  </h1>", unsafe_allow_html=True)
    st.markdown('---')
    st.markdown("<h2 style='text-align: center; color: #2E1F84; font-size: 40px;'>Probabilidades dos Jogos ⚽<br>  </h1>", unsafe_allow_html=True)
    st.markdown('---')

    times = ["Vasco","São Paulo","Palmeiras","Fortaleza","Flamengo","Corinthians","Bahia","Botafogo",
             "Atlético Goianiense","Atlético Paranaense","Atlético Mineiro","Cruzeiro","Internacional",
             "Red Bull Bragantino","Cuiabá","Fluminense","Fortaleza","Juventude","Criciúma","Vitória","Grêmio"]
    time1 = st.selectbox("Time mandante:", times)
    time2 = st.selectbox("Time visitante: ", times)

    st.markdown(
        """
        <style>
        .stButton>button {
            background-color: #00FFB3 !important;
            color: #2E1F84 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button('Calcular Probabilidades'):
      if time1 not in full['time'].unique() or time2 not in full['time'].unique():
        st.write("Um ou ambos os times informados não foram encontrados.")
      else:
        # Dicionário para armazenar as previsões de cada equipe
        previsoes = {}

        # Calcular as previsões apenas para os times escolhidos pelo usuário
        for time in [time1, time2]:
            gols_feitos_casa = list(map(int, eval(full.loc[full['time'] == time, 'gf_casa'].values[0])))
            gols_sofridos_casa = list(map(int, eval(full.loc[full['time'] == time, 'gs_casa'].values[0])))
            gols_feitos_fora = list(map(int, eval(full.loc[full['time'] == time, 'gf_fora'].values[0])))
            gols_sofridos_fora = list(map(int, eval(full.loc[full['time'] == time, 'gs_fora'].values[0])))

            previsoes_equipe = {}
            for tipo_gol, dados in zip(["Gols feitos em casa", "Gols sofridos em casa", "Gols feitos fora de casa",
                                        "Gols sofridos fora de casa"],
                                       [gols_feitos_casa, gols_sofridos_casa, gols_feitos_fora, gols_sofridos_fora]):
                a0, a1 = regressao(np.arange(1, len(dados) + 1), dados)
                previsao = a0 + a1 * 13  # Previsão para x = 20
                previsoes_equipe[tipo_gol] = previsao

            previsoes[time] = previsoes_equipe

        # Exibir as previsões apenas para os times escolhidos pelo usuário
        # for time in [time1, time2]:
        # print(f"Previsão para {time}:")
        # for tipo_gol, previsao in previsoes[time].items():
        # print(f"{tipo_gol}: {previsao}")

        # Calcula as médias das previsões para os diferentes tipos de gols
        media_entre_gols = {}
        for tipo_gol in previsoes[time1]:
            media_time1 = previsoes[time1][tipo_gol]
            media_time2 = previsoes[time2][tipo_gol]
            media_entre_gols[tipo_gol] = (media_time1 + media_time2) / 2

        # Exibir as médias entre gols para os diferentes tipos de gols
        # print("\nMédias entre gols para os times fornecidos:")
        # for tipo_gol, media in media_entre_gols.items():
        # print(f"{tipo_gol}: {media}")

        # Calcula a expectativa de gol para cada time
        expectativa_gol = {}
        for time, previsoes_time in previsoes.items():
            expectativa_gol[time] = {}
            for tipo_gol, previsao in previsoes_time.items():
                media = media_entre_gols.get(tipo_gol)
                if media is not None:
                    tipo_gol_formatado = tipo_gol.replace("Gols feitos", "Força de ataque").replace("Gols sofridos",
                                                                                                    "Força de defesa")
                    expectativa_gol[time][tipo_gol_formatado] = previsao / media

        # Exibe a divisão das previsões pelos valores médios
        # print("\nDivisão das previsões pelos valores médios:")
        # for time, divisoes in expectativa_gol.items():
        # print(f"\nExpectativa de gol para {time}:")
        # for tipo_gol, divisao in divisoes.items():
        # print(f"{tipo_gol}: {divisao}")

        # Calcula os valores de m1 e m2
        forca_ataque_time1_em_casa = expectativa_gol[time1]["Força de ataque em casa"]
        forca_defesa_time2_fora = expectativa_gol[time2]["Força de defesa fora de casa"]
        media_gols_feito_casa = media_entre_gols["Gols feitos em casa"]

        m1 = forca_ataque_time1_em_casa * forca_defesa_time2_fora * media_gols_feito_casa
        # print("\nm1:", m1)

        forca_ataque_time2_fora = expectativa_gol[time2]["Força de ataque fora de casa"]
        forca_defesa_time1_em_casa = expectativa_gol[time1]["Força de defesa em casa"]
        media_gols_feito_fora = media_entre_gols["Gols feitos fora de casa"]

        m2 = forca_ataque_time2_fora * forca_defesa_time1_em_casa * media_gols_feito_fora


        # print("m2:", m2)

        # Calcula probabilidade
        def f(x, y):
            return (((np.e ** (-m1)) * m1 ** (x)) / (math.factorial(x))) * (
                    ((np.e ** (-m2)) * (m2 ** (y))) / (math.factorial(y)))


        prob_vitoria_time1 = sum(f(x, y) for x in range(6) for y in range(6) if x > y)
        prob_empate = sum(f(x, y) for x in range(6) for y in range(6) if x == y)
        prob_vitoria_time2 = sum(f(x, y) for x in range(6) for y in range(6) if x < y)

        imagens = {"Vasco": "https://gifs.eco.br/wp-content/uploads/2023/11/imagens-do-vasco-da-gama-png-2.png",
                   "São Paulo": "https://logodownload.org/wp-content/uploads/2016/09/sao-paulo-fc-logo.png",
                   "Palmeiras": "https://logodownload.org/wp-content/uploads/2015/05/palmeiras-logo-0.png",
                   "Fortaleza": "https://cdn.freebiesupply.com/logos/thumbs/2x/fortaleza-esporte-clube-de-fortaleza-ce-logo.png",
                   "Flamengo": "https://images.flamengo.com.br/public/images/artigos/32947/1648959889.png",
                   "Corinthians": "https://cartolafcmix.com/wp-content/uploads/2022/04/corinthians.png",
                   "Bahia": "https://logodownload.org/wp-content/uploads/2017/02/bahia-ec-logo-0.png",
                   "Botafogo": "https://logodownload.org/wp-content/uploads/2016/11/botafogo-logo-0.png",
                   "Atlético Goianiense": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Atl%C3%A9tico_Goianiense.svg/1200px-Atl%C3%A9tico_Goianiense.svg.png",
                   "Atlético Paranaense": "https://static.wikia.nocookie.net/logopedia/images/d/d8/Athletico-2018.png/revision/latest/scale-to-width-down/800?cb=20210603162546",
                   "Atlético Mineiro": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Clube_Atl%C3%A9tico_Mineiro_logo.svg/1810px-Clube_Atl%C3%A9tico_Mineiro_logo.svg.png",
                   "Cruzeiro": "https://upload.wikimedia.org/wikipedia/commons/b/bc/Logo_Cruzeiro_1996.png",
                   "Internacional": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Escudo_do_Sport_Club_Internacional.svg/2048px-Escudo_do_Sport_Club_Internacional.svg.png",
                   "Red Bull Bragantino": "https://lh3.ggpht.com/-2H8TG2xgkNM/XioxlJNOhuI/AAAAAAAAExA/Ev9a8vKC-VUstZYHNGP-7Ju9hbvi6BbqQCEwYBhgL/s0/bragantino.png",
                   "Cuiabá": "https://logodetimes.com/times/cuiaba/logo-cuiaba-2048.png",
                   "Fluminense": "https://imagepng.org/escudo-do-fluminense-fc/escudo-fluminense-fc-1/",
                   "Juventude": "https://logodownload.org/wp-content/uploads/2017/02/ec-juventude-logo-escudo.png",
                   "Criciúma": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/EscudoCriciumaEC.svg/2560px-EscudoCriciumaEC.svg.png",
                   "Vitória": "https://logodownload.org/wp-content/uploads/2017/02/ec-vitoria-logo-1.png",
                   "Grêmio": "https://gifs.eco.br/wp-content/uploads/2023/07/imagens-do-escudo-gremio-png-3.png"}



        if time1 and time2:
            st.write("---")
            if time1 in imagens:
                st.markdown(
                    f"""
                            <div style='text-align: center;'>
                                <h1 style='color: #2E1F84;'>{time1}</h1>
                                <h1 style='color: #2E1F84;'>{prob_vitoria_time1 * 100:.2f}%</h1>
                                <img src='{imagens[time1]}' width='400'>
                            </div>
                         """, unsafe_allow_html=True)
            st.write("---")

            st.markdown(
                f"""
                    <div style='text-align: center;'>
                        <h1 style='color: #FFBE0B;'>Empate</h1>
                        <h2 style='color: #FFBE0B;'>{prob_empate * 100:.2f}%</h2>
                    </div>
                    """, unsafe_allow_html=True)

            st.write("---")

            if time2 in imagens:
                st.markdown(
                    f"""
                            <div style='text-align: center;'>
                                <h1 style='color: #2E1F84;'>{time2}</h1>
                                <h1 style='color: #2E1F84;'>{prob_vitoria_time2 * 100:.2f}%</h1>
                                <img src='{imagens[time2]}' width='400'>
                            </div>
                            """, unsafe_allow_html=True)
            st.write("---")




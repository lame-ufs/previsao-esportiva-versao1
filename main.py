import pandas as pd
import numpy as np
from scipy.stats import poisson
import seaborn as sns
import streamlit as st



# Carregar os dados do arquivo CSV
Dados = pd.read_csv("data_teams.csv")

st.sidebar.header('Menu')
paginas = ['Previsão Brasileirão Série A', 'Tabelas']
pagina = st.sidebar.radio('Selecione a página', paginas)

if pagina == 'Previsão Brasileirão Série A':
    st.markdown("<h2 style='text-align: center; color: #FFBE0B; font-size: 32px;'>Brasileirão Série A 2024 🏆  </h1>", unsafe_allow_html=True)
    st.markdown('---')
    st.markdown("<h2 style='text-align: center; color: #2E1F84; font-size: 40px;'>Probabilidades dos Jogos ⚽<br>  </h1>", unsafe_allow_html=True)
    st.markdown('---')

    time1 = ['São Paulo', 'Flamengo', 'Fortaleza', 'Juventude', 'Cruzeiro', 'Internacional', 'Vitória',
                 'Atlético Goianiense', 'Palmeiras', 'Botafogo']
    time2 = ['Red Bull Bragantino', 'Cuiabá', 'Fluminense', 'Grêmio', 'Corinthians', 'Vasco', 'Criciúma',
                  'Athletico Paranaense', 'Bahia', 'Atlético Mineiro']
    mandante = st.selectbox("Time mandante:", ["Selecione o time"] +time1)
    visitante = st.selectbox("Time visitante: ", ["Selecione o time"] + time2)

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
      if mandante not in Dados['time'].unique() or visitante not in Dados['time'].unique():
        st.write("Um ou ambos os times informados não foram encontrados.")
      else:
          def Resultado_Real_Jogos(Dados):
              resC, resF = [], []
              times = Dados['time'].unique()

              for time in times:
                  Gols_T = [eval(Dados[Dados['time'] == time]['gf_casa'].values[0]),
                            eval(Dados[Dados['time'] == time]['gs_casa'].values[0]),
                            eval(Dados[Dados['time'] == time]['gf_fora'].values[0]),
                            eval(Dados[Dados['time'] == time]['gs_fora'].values[0])]

                  Res_jogos_C = [1 if gm > gs else 0 if gm < gs else 2 for gm, gs in zip(Gols_T[0], Gols_T[
                      1])]  # Catalogando vitorias, empates, derrotas para os jogos em casa
                  resC.append(Res_jogos_C)

                  Res_jogos_F = [1 if gm > gs else 0 if gm < gs else 2 for gm, gs in zip(Gols_T[2], Gols_T[
                      3])]  # Catalogando vitorias, empates, derrotas para os jogos fora de casa
                  resF.append(Res_jogos_F)

              return resC, resF

          Dados['Res_Casa'], Dados['Res_Fora'] = Resultado_Real_Jogos(Dados)


          def Gols_dos_times(Mandante, Visitante, Dados):
              Gols_A, Gols_B = [], []
              x = min(len(eval(Dados[Dados['time'] == Mandante]['gf_casa'].values[0])),
                      len(eval(Dados[Dados['time'] == Visitante]['gf_fora'].values[0])))
              # Coletando gols
              Gols_A.append(eval(Dados[Dados['time'] == Mandante]['gf_casa'].values[0])[:x])
              Gols_A.append(eval(Dados[Dados['time'] == Mandante]['gs_casa'].values[0])[:x])
              Gols_A.append(eval(Dados[Dados['time'] == Mandante]['gf_fora'].values[0])[:x])
              Gols_A.append(eval(Dados[Dados['time'] == Mandante]['gs_fora'].values[0])[:x])
              #
              Gols_B.append(eval(Dados[Dados['time'] == Visitante]['gf_casa'].values[0])[:x])
              Gols_B.append(eval(Dados[Dados['time'] == Visitante]['gs_casa'].values[0])[:x])
              Gols_B.append(eval(Dados[Dados['time'] == Visitante]['gf_fora'].values[0])[:x])
              Gols_B.append(eval(Dados[Dados['time'] == Visitante]['gs_fora'].values[0])[:x])

              return [Gols_A, Gols_B]


          def Medias(Mandante, Visitante, Dados):
              equipes = Gols_dos_times(Mandante, Visitante, Dados)
              medias_t1 = [np.mean(equipe[:10]) for equipe in equipes[0]]
              medias_t2 = [np.mean(equipe[:10]) for equipe in equipes[1]]
              return medias_t1, medias_t2


          def Medias_do_Campeonato(Dados):
              mg1 = mg2 = mg3 = mg4 = 0
              times = Dados['time'].unique()
              Gols = []
              for time in times:
                  mg1 += np.mean(eval(Dados[Dados['time'] == time]['gf_casa'].values[0]))
                  mg2 += np.mean(eval(Dados[Dados['time'] == time]['gs_casa'].values[0]))
                  mg3 += np.mean(eval(Dados[Dados['time'] == time]['gf_fora'].values[0]))
                  mg4 += np.mean(eval(Dados[Dados['time'] == time]['gs_fora'].values[0]))
              medias = [mg1 / len(times), mg2 / len(times), mg3 / len(times), mg4 / len(times)]
              return medias


          def Forca_Ataque_Defesa(Mandante, Visitante, Dados):
              M_times = Medias(Mandante, Visitante, Dados)
              geral = Medias_do_Campeonato(Dados)
              F_timeA = [np.mean(media) for media in M_times[0]]
              F_timeB = [np.mean(media) for media in M_times[1]]

              return [F_timeA, F_timeB]


          def Expectativa_de_Gol(Mandante, Visitante, Dados):
              FA, FB = Forca_Ataque_Defesa(Mandante, Visitante, Dados)
              geral = Medias_do_Campeonato(Dados)
              E_timeA = FA[0] * FB[3] / geral[0]
              E_timeB = FB[2] * FA[1] / geral[2]
              return E_timeA, E_timeB


          # Funções Probabilidade baseada no desempenho dos times
          # iremos analizar os resultados das partidas dos dois times para ver quantas vitorias, derrotas e empates cada time teve em casa e fora
          def Desempenho(Mandante, Visitante, Dados):
              resC = Dados[Dados['time'] == Mandante]['Res_Casa'].values[0]
              resF = Dados[Dados['time'] == Visitante]['Res_Fora'].values[0]

              # Contagem de resultados para casa
              V_casa = np.sum(np.array(resC) == 1)
              D_casa = np.sum(np.array(resC) == 0)
              E_casa = np.sum(np.array(resC) == 2)
              # Contagem de resultados para fora
              V_fora = np.sum(np.array(resF) == 1)
              D_fora = np.sum(np.array(resF) == 0)
              E_fora = np.sum(np.array(resF) == 2)

              return [[V_casa, D_casa, E_casa], [V_fora, D_fora, E_fora]]


          # utilizaremos os valores encontados da função Desempenho para determinar o desempenho dos times em casa e fora
          # esse desempenho será dado por : nº de (Vitorias, empates ou derrotas em casa) / nº de partidas jogadas em casa
          # essa condicional irá utilizar o desempenho do time nos ultimos jogos para ajustar o probabilidade encontrada inicialmente
          def Ajuste(Mandante, Visitante, Dados):
              desempenho = Desempenho(Mandante, Visitante, Dados)
              c1 = desempenho[0]
              c2 = desempenho[1]
              # Somando os resultados de vitórias, derrotas e empates para casa e fora
              totais = [sum(x) for x in zip(c1, c2)]
              # Calcular a proporção
              c1 = [c / t if t != 0 else np.mean(c1) for c, t in zip(c1, totais)]
              c2 = [c / t if t != 0 else np.mean(c2) for c, t in zip(c2, totais)]
              # Normalizar as proporções para somarem 1
              c1 = [c / sum(c1) for c in c1]
              c2 = [c / sum(c2) for c in c2]
              # Calcular ajustes
              ajuste_V = c1[0] * c2[0]
              ajuste_D = c1[1] * c2[1]
              ajuste_E = c1[2] * c2[2]


              return [ajuste_V, ajuste_D, ajuste_E]


          # FUNÇÕES PARA CALCULAR PROBABILIDADES E APLICAR AJUSTES
          def f(x, y, EGA, EGB):  # EGA - expectativa de gol do time A; # EGB - expectativa de gol do time B
              return poisson.pmf(x, EGA) * poisson.pmf(y, EGB)


          def Previsao_jogo(Mandante, Visitante, Dados):
              timeA = timeB = empate = 0
              Condicional = Ajuste(Mandante, Visitante, Dados)
              EGA, EGB = Expectativa_de_Gol(Mandante, Visitante, Dados)
              # priori
              probs = np.array([[f(i, j, EGA, EGB) for j in range(9)] for i in range(9)])
              timeA = np.tril(probs, -1).sum()  # Soma todos os elementos abaixo da diagonal principal
              timeB = np.triu(probs, 1).sum()  # Soma todos os elementos acima da diagonal principal
              empate = np.trace(probs)  # Soma todos os elementos da diagonal principale
              # Apricando Condicional
              Prob = [timeA, timeB, empate]
              equipes = [equipe * ajuste for equipe, ajuste in zip(Prob, Condicional)]
              # Normalizar para que a soma seja 1
              total = sum(equipes)
              equipes = [equipe / total for equipe in equipes]
              #
              timeA, timeB, empate = equipes
              return [timeA, timeB, empate]


    imagens = {"Vasco": "https://logodownload.org/wp-content/uploads/2016/09/vasco-logo-4.png",
                   "São Paulo": "https://logodownload.org/wp-content/uploads/2016/09/sao-paulo-logo-escudo-768x766.png",
                   "Palmeiras": "https://logodownload.org/wp-content/uploads/2015/05/palmeiras-logo.png",
                   "Fortaleza": "https://logodownload.org/wp-content/uploads/2018/08/fortaleza-ec-logo-escudo-9-768x806.png",
                   "Flamengo": "https://logodownload.org/wp-content/uploads/2016/09/flamengo-logo-escudo-novo-5.png",
                   "Corinthians": "https://cartolafcmix.com/wp-content/uploads/2022/04/corinthians.png",
                   "Bahia": "https://logodownload.org/wp-content/uploads/2017/02/bahia-ec-logo-01-768x768.png",
                   "Botafogo": "https://logodownload.org/wp-content/uploads/2016/11/botafogo-logo-escudo-768x866.png",
                   "Atlético Goianiense": "https://logodownload.org/wp-content/uploads/2017/02/atletico-goianiense-logo-4.png",
                   "Athletico Paranaense": "https://logodownload.org/wp-content/uploads/2016/10/atletico-paranaense-logo-escudo-768x768.png",
                   "Atlético Mineiro": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Clube_Atl%C3%A9tico_Mineiro_logo.svg/1810px-Clube_Atl%C3%A9tico_Mineiro_logo.svg.png",
                   "Cruzeiro": "https://upload.wikimedia.org/wikipedia/commons/b/bc/Logo_Cruzeiro_1996.png",
                   "Internacional": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Escudo_do_Sport_Club_Internacional.svg/2048px-Escudo_do_Sport_Club_Internacional.svg.png",
                   "Red Bull Bragantino": "https://lh3.ggpht.com/-2H8TG2xgkNM/XioxlJNOhuI/AAAAAAAAExA/Ev9a8vKC-VUstZYHNGP-7Ju9hbvi6BbqQCEwYBhgL/s0/bragantino.png",
                   "Cuiabá": "https://logodetimes.com/times/cuiaba/logo-cuiaba-2048.png",
                   "Fluminense": "https://imagepng.org/escudo-do-fluminense-fc/escudo-fluminense-fc-1/",
                   "Juventude": "https://logodownload.org/wp-content/uploads/2017/02/ec-juventude-logo-escudo.png",
                   "Criciúma": "https://logodownload.org/wp-content/uploads/2017/02/criciuma-logo-escudo-1.png",
                   "Vitória": "https://logodownload.org/wp-content/uploads/2017/02/ec-vitoria-logo-1.png",
                   "Grêmio": "https://logodownload.org/wp-content/uploads/2017/02/gremio-logo-escudo-2.png"}

    previsao = Previsao_jogo(mandante, visitante, Dados)
    if mandante and visitante:
        st.write("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            if mandante in imagens:
                st.markdown(f"""
                                    <div style='text-align: center;'>
                                        <h1 style='color: #2E1F84;'>{mandante}</h1>
                                        <h1 style='color: #2E1F84;'>{previsao[0]*100:.2f}%</h1>
                                        <img src='{imagens[mandante]}'  width='200'> </div>
                                 """, unsafe_allow_html=True)

        with col2:
            st.markdown(f""" <div style='text-align: center;'>
                                    <h1 style='color: #FFBE0B;'>Empate</h1>
                                    <h1 style='color: #FFBE0B;'>{previsao[2]*100:.2f}%</h1>
                                     </div>""", unsafe_allow_html=True)


        with col3:
            if visitante in imagens:
                st.markdown(f"""<div style='text-align: center;'>
                                <h1 style='color: #2E1F84;'>{visitante}</h1>
                                <h1 style='color: #2E1F84;'>{previsao[1]*100:.2f}%</h1>
                                <img src='{imagens[visitante]}'  width='200'></div>""", unsafe_allow_html=True)

        st.write("---")

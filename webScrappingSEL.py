import csv
from selenium import webdriver
from unidecode import unidecode
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

def data_collect(results, conditions): #Minera os dados no site e adiciona os resultados das partidas na lista
    elements_tr = browser.find_elements(By.CSS_SELECTOR, 'tr.parent')

    for tr in elements_tr:

        td_result = tr.find_elements(By.CSS_SELECTOR, 'td.result')
        result = td_result[0].find_element(By.TAG_NAME, 'a').text

        condition = tr.find_elements(By.TAG_NAME, 'td')[3].text

        conditions.append(condition)
        results.append(result)

    return results, conditions

def add_data(rs, cs): #Adiciona os dados coletados e adiciona em arrays
    home_gf_team, away_gf_team, home_ga_team, away_ga_team = [], [], [], []

    for i, r in enumerate(rs):
        if len(r) > 2 and r != 'ADI':
            c = cs[i].replace('(', '').replace(')', '')
            
            if c == 'C':
                home_gf_team.append(int(r[0]))
                home_ga_team.append(int(r[2]))
            else:
                away_gf_team.append(int(r[2]))
                away_ga_team.append(int(r[0]))

    return home_gf_team, home_ga_team, away_gf_team, away_ga_team

def clear_file(name): #Limpa o arquivo
    with open(name, 'w', newline='', encoding='utf-8') as _:
        pass

def scrapping(team): #Faz a raspagem dos dados
    team = unidecode(team).strip().lower().replace(' ', '-')
    link = "https://www.ogol.com.br/equipe/" + team + "/todos-os-jogos?grp=1" #Cria o link a ser acessado
    browser.get(link) #Acessa o link
    
    results, conditions = data_collect([], []) #Guarda os dados em duas listas, uma de condição (Casa ou Fora) e uma de resultados dos jogos.

    link += '&page=2'
    browser.get(link)
    
    results, conditions = data_collect(results, conditions)

    #Listas que irao guardar os dados do time
    hgf_team, hga_team, agf_team, aga_team = add_data(results, conditions)

    return (hgf_team, hga_team, agf_team, aga_team)

def add_in_files(): #Adiciona os dados nos arquivos csv

    with open('teams.txt', 'r', encoding='utf-8') as teams_file:
        lines = teams_file.readlines()
        clear_file('data_teams.csv')
        clear_file('df_teams.csv')

        with open('df_teams.csv', 'a', newline='', encoding='utf-8') as df_file:
            df_file.write("time,gf_casa,gs_casa,gf_fora,gs_fora\n")

        with open('data_teams.csv', 'a', newline='', encoding='utf-8') as df_file:
            df_file.write("time,gf_casa,gs_casa,gf_fora,gs_fora\n")

        for line in lines:
            team = line.strip().strip('\n')
            hgf_team, hga_team, agf_team, aga_team = scrapping(team)

            row = [hgf_team, hga_team, agf_team, aga_team]
            team = team.split('/')[0]

            with open('data_teams.csv', 'a', newline='', encoding='utf-8') as data_file:
                writer = csv.writer(data_file)
                data_file.write(f'{team},')
                writer.writerow(row)
            
            with open('df_teams.csv', 'a', newline='', encoding='utf-8') as df_file:
                row = list(map(sum, row))
                row.insert(0, team)
                writer = csv.writer(df_file)
                writer.writerow(row)
                
i = time.time()

# Inicializar o navegador Firefox com o driver mais recente
browser = webdriver.Firefox()
with browser as browser: #Abre o navegador escolhido
    add_in_files()

f = time.time()

print(f"Execution completed! Time: {((f-i)/60):.2f} mins")
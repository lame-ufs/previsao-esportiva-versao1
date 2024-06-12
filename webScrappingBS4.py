import csv
from bs4 import BeautifulSoup
from unidecode import unidecode
import requests
import time

def data_collect(soup, results, conditions): #Minera os dados no site e adiciona os resultados das partidas na lista
    elements = soup.find_all('tr', class_= 'parent')

    for element in elements:
        result = element.find('td', class_= 'result').text
        condition = element.find_all('td')[3].text

        results.append(result)
        conditions.append(condition)

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
    
    page = requests.get(link, headers= headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    results, conditions = data_collect(soup, [], []) #Guarda os dados em duas listas, uma de condição (Casa ou Fora) e uma de resultados dos jogos.

    link += '&page=2'

    page = requests.get(link, headers= headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    results, conditions = data_collect(soup, results, conditions)

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

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0'}
add_in_files()

f = time.time()

print(f"Execution completed! Time: {((f-i)/60):.2f} mins")
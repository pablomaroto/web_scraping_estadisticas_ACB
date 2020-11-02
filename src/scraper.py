import urllib.request
from bs4 import BeautifulSoup
import pandas as pd

def clean_standard(txt):
    new_txt = str(txt)
    new_txt = new_txt.split('<')[1]
    new_txt = new_txt.split('>')[1]
    return new_txt

def clean_standard_alt(txt):
    new_txt = str(txt)
    new_txt = new_txt.split('<')[1]
    new_txt = new_txt.split('>')[1]
    new_txt = new_txt.split()[0]
    return new_txt

def clean_club(club):
    new_club = str(club)
    new_club = new_club.split('<')[3]
    new_club = new_club.split('>')[1]
    return new_club

def get_url(url):
    url = str(url)
    url = url.split()[1]
    url = url.split('=')[1]
    url = url[1:-1]
    return url

def get_player_url(url):
    url = str(url)
    url = url.split()[1]
    url = url.split('=')[1]
    url = url[1:-1]
    url = url.split('/')[3]
    url = url.split('-')[0]
    url = '/jugador/temporada-a-temporada/id/'+url
    return url


columns = ['nombre',
            'posicion',
            'altura',
            'nacimiento',
            'licencia',
            'temporada',
            'club',
            'partidos_jugados',
            'minutos_jugados',
            '5i',
            'puntos_totales',
            'puntos_maximos',
            'tiros_de_3_convertidos',
            'tiros_de_3_intentados',
            'tiros_de_3_%',
            'tiros_de_2_convertidos',
            'tiros_de_2_intentados',
            'tiros_de_2_%',
            'tiros_de_1_convertidos',
            'tiros_de_1_intentados',
            'tiros_de_1_%',
            'rebotes_ofensivos',
            'rebotes_defensivos',
            'rebotes_totales',
            'asistencias',
            'recuperaciones',
            'perdidas',
            'tapones_a_favor',
            'tapones_en_contra',
            'mates',
            'faltas_cometidas',
            'faltas_recibidas',
            '+/-',
            'valoracion',
            'victorias',
            'derrotas']

df = pd.DataFrame(columns = columns)

url_acb = 'http://www.acb.com'
url = 'http://www.acb.com/club'

try:
    print('Opening club list.')
    ourUrl = urllib.request.urlopen(url)
except:
    print('ERROR opening club list. Url: '+str(url))
    exit

soup = BeautifulSoup(ourUrl, 'html.parser')

club_list = soup.find('div', {'class':'listado_clubes'})
club_list_url = []
for club in club_list.find_all('article', {'class':'club'}):
    url_club = club.find('a')
    url_club = url_acb+get_url(url_club)
    club_list_url.append(url_club)


for club_url in club_list_url:
    try:
        print('Opening club player list.')
        ourUrl = urllib.request.urlopen(club_url)
    except:
        print('ERROR opening club player list. Url: '+str(club_url))
        continue

    soup = BeautifulSoup(ourUrl, 'html.parser')

    player_list = soup.find('section', {'class':'contenido_central contenido_central_equipo'})
    player_list_url = []
    for player in player_list.find_all('article', {'class':'caja_miembro_plantilla caja_jugador_medio_cuerpo'}):
        url_player = player.find('a')
        url_player = url_acb+get_player_url(url_player)
        player_list_url.append(url_player)

    for player in player_list.find_all('article', {'class':'caja_miembro_plantilla caja_jugador_cara'}):
        url_player = player.find('a')
        url_player = url_acb+get_player_url(url_player)
        player_list_url.append(url_player)

    for players in player_list.find_all('table', {'class':'roboto defecto tabla_plantilla plantilla_bajas clasificacion tabla_ancho_completo'}):
        for player in players.find_all('a'):
            url_player = player
            url_player = url_acb+get_player_url(url_player)
            if ("/jugador/" in url_player):
                player_list_url.append(url_player)


    for player_url in player_list_url:
        try:
            print('Opening player stats.')
            ourUrl = urllib.request.urlopen(player_url)
        except:
            print('ERROR opening player stats. Url: '+str(player_url))
            continue

        soup = BeautifulSoup(ourUrl, 'html.parser')

        player_name = soup.find('h1', {'class':'f-l-a-100 roboto_condensed_bold mayusculas'})
        position = soup.find('div', {'class':'datos_basicos posicion roboto_condensed'})
        position = position.find('span', {'class':'roboto_condensed_bold'})
        height = soup.find('div', {'class':'datos_basicos altura roboto_condensed'})
        height = height.find('span', {'class':'roboto_condensed_bold'})
        birth_date = soup.find('div', {'class':'datos_secundarios fecha_nacimiento roboto_condensed'})
        birth_date = birth_date.find('span', {'class':'roboto_condensed_bold'})
        license = soup.find('div', {'class':'datos_secundarios licencia roboto_condensed'})
        license = license.find('span', {'class':'roboto_condensed_bold'})

        table = soup.find('table', {'data-toggle':'table-estadisticas-jugador'})
        table = table.find('tbody')

        for stats in table.find_all('tr'):
            row = {}
            row_values = []
            row_values.append(str(player_name))
            row_values.append(str(position))
            row_values.append(str(height))
            row_values.append(str(birth_date))
            row_values.append(str(license))
            for stats_data in stats.find_all('td'):
                row_values.append(str(stats_data))

            for key in columns:
                for value in row_values:
                    row[key] = value
                    row_values.remove(value)
                    break


            df = df.append(row, ignore_index=True)


df = df[df.club != '<td class="nombre_jugador">Totales</td>']
df = df[df.club != '<td class="nombre_jugador">Promedios</td>']

for column in df:
    if column == 'club':
        df[column] = df[column].apply(clean_club)
    elif column == 'altura' or column == 'nacimiento':
        df[column] = df[column].apply(clean_standard_alt)
    else:
        df[column] = df[column].apply(clean_standard)



df.to_csv('../csv/estadisticas_jugadores_ACB.csv', index = False)

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from pprint import pprint
import sqlite3
from geopy.geocoders import Nominatim
import geopandas as gpd
from shapely.geometry import Point


def getDadosCEP(cep):
		url = (f'http://www.viacep.com.br/ws/{cep}/json')
		
		req = requests.get(url)
		if req.status_code == 200:
			dados_json = json.loads(req.text)
			return dados_json
		else:
			print('Erro ao buscar CEP')
               
def getCEP(rua):
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    headers = {'User-Agent': 'MyGeocodingApp/1.0 (ggsnasser@gmail.com)'}
    
    params = {
        'q': rua + ', ' + "Regiao Metropolitana de Sao Paulo",            
        'format': 'json',       
        'addressdetails': 1
    }
    
    # Fazendo a requisição com o cabeçalho User-Agent
    response = requests.get(nominatim_url, headers=headers, params=params)
    return response.json()[0]['address']['postcode']

def geocode_address(address):
    try:
        geolocator = Nominatim(user_agent="Creating a conversion table for São Paulo")
        location = geolocator.geocode(address)
        
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except:
        return None
    
def find_sector(coordenadas, setores_gdf):
    # Criar um ponto com a lat e long fornecida
    try:
        lat, lon = coordenadas
        point = Point(lon, lat)  # Note que o formato é (longitude, latitude)
        
        # Verificar qual setor contém o ponto
        setor_encontrado = setores_gdf[setores_gdf.contains(point)]
        
        if not setor_encontrado.empty:
            return setor_encontrado["CD_SETOR"].values[0]
        else:
            return None
    except:
        return None
    
def get_setor(rua):
    setores = gpd.read_file('dados\geo\SP_Malha_Preliminar_2022.shp')
    sp = setores[setores["NM_MUN"] == "São Paulo"]
    sp = sp.to_crs(epsg=4326)
    coordenadas = geocode_address(rua)
    setor = find_sector(coordenadas, sp)
    return setor
    

def scraper(bairro):
    driver = webdriver.Chrome()

    url = 'https://www.quintoandar.com.br/comprar/imovel/'+bairro+'-sao-paulo-sp-brasil'
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    numero = soup.find("div", class_="Toolbar_title__hZZcF").text.split(" ")[0]

    driver.get('https://www.quintoandar.com.br/comprar/imovel/'+bairro+'-sao-paulo-sp-brasil')
    time.sleep(5)

    # for i in range(int(numero.replace('.', ''))//12):
    for i in range(2):
        try:
            ver_mais_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Ver mais')]")
            ver_mais_button.click()  # Clica no botão
            time.sleep(3)  # Aguarde o conteúdo carregar após o clique
        except:
            pass

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    soup = soup.find('html')
    soup = soup.prettify()
    return soup

def find_rua_imovel(imovel):
    rua = imovel.find("div", class_="Cozy__FindHouseCard-Container").text
    rua = rua.split("São Paulo")[0].split('\n\n')[-1].lstrip()
    rua = rua.split(",")[0]
    return rua

def find_preco_imovel(imovel):
    valor = imovel.find("div", class_="Cozy__FindHouseCard-Container").text
    valor = valor.split("R$")[1]
    return re.sub(r'\D', '', valor)

def find_m2_imovel(imovel):
    img_tag = imovel.find('img', class_='ProgressiveImage_image__1QoR0')
    alt_text = img_tag['alt']
    alt_text = alt_text.split("m²")[0].split(" ")
    return alt_text[-1]

def find_endereco(imovel):
    bairro = imovel.find("h2", class_="CozyTypography xih2fc _72Hu5c Ci-jp3").text
    bairro = bairro.replace('\n','')
    bairro = bairro.replace(" · ", ", ")
    bairro = bairro.lstrip()
    endereco = bairro.rstrip()
    return endereco

def find_bairro(imovel):
    bairro = imovel.find("h2", class_="CozyTypography xih2fc _72Hu5c Ci-jp3").text
    bairro = bairro.replace('\n','')
    bairro = bairro.replace(" · ", ", ")
    bairro = bairro.lstrip()
    bairro = bairro.rstrip()
    bairro = bairro.split(", ")[1]
    return bairro

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

def create_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cep TEXT NOT NULL,
    setor TEXT NOT NULL,
    rua TEXT NOT NULL,
    bairro TEXT NOT NULL,
    cidade TEXT NOT NULL,
    estado TEXT NOT NULL,
    regiao TEXT NOT NULL,
    preco FLOAT NOT NULL,
    m2 FLOAT NOT NULL,
    preco_m2 FLOAT NOT NULL
    )
    ''')
    conn.commit()

def add_data(cep, setor, rua, bairro, cidade, estado, regiao, preco, m2, preco_m2):
    cursor.execute('''
    INSERT INTO data (cep, setor, rua, bairro, cidade, estado, regiao, preco, m2, preco_m2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (cep, setor, rua, bairro, cidade, estado, regiao, preco, m2, preco_m2))
    conn.commit()

def remove_data(id):
    cursor.execute('''
    DELETE FROM data WHERE id = ?
    ''', (id,))
    conn.commit()

def delete_all():
    cursor.execute('''
    DELETE FROM data
    ''')
    conn.commit()

def get_id(cep):
    cursor.execute('''
    SELECT id FROM data WHERE cep = ?
    ''', (cep,))
    data = cursor.fetchall()
    return data

def extract_data(cep):
    dados = getDadosCEP(cep)
    bairro = dados['bairro']
    cidade = dados['localidade']
    estado = dados['uf']
    regiao = dados['regiao']
    bairro = bairro.replace(" ", "-").lower()
    soup = scraper(bairro)
    soup = BeautifulSoup(soup, 'html.parser')
    casas = soup.find_all(attrs={"data-testid": "house-card-container"})
    for casa in casas:
        preco = find_preco_imovel(casa)
        m2 = find_m2_imovel(casa)
        bairro = find_bairro(casa)
        rua = find_rua_imovel(casa)
        endereco = rua + ", São Paulo, Brasil, Região Metropolitana de São Paulo"
        setor = get_setor(endereco)
        preco_m2 = float(preco) / float(m2)
        
        # Check if the data already exists
        cursor.execute('''
        SELECT id FROM data 
        WHERE cep = ? AND bairro = ? AND preco = ? AND m2 = ?
        ''', (cep, bairro, preco, m2))
        
        if cursor.fetchone() is None:
            # Data doesn't exist, so insert it
            cep = getCEP(rua)
            add_data(cep, setor, rua, bairro, cidade, estado, regiao, preco, m2, preco_m2)

def precos_medios():
    cursor.execute('''
    SELECT bairro, AVG(preco_m2) AS preco_medio_m2
    FROM data
    GROUP BY bairro
    ''')
    return cursor.fetchall()

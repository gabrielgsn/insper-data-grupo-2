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
from shapely.geometry import Point, box


def getDadosCEP(cep):
		url = (f'http://www.viacep.com.br/ws/{cep}/json')
		
		req = requests.get(url)
		if req.status_code == 200:
			dados_json = json.loads(req.text)
			return dados_json
		else:
			print('Erro ao buscar CEP')
               
def getCEP(rua):
    try:
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
    except:
        return None

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
    try:
        setores = gpd.read_file('dados\geo\SP_Malha_Preliminar_2022.shp')
        sp = setores[setores["NM_MUN"] == "São Paulo"]
        sp = sp.to_crs(epsg=4326)
        coordenadas = geocode_address(rua)
        setor = find_sector(coordenadas, sp)
        return setor
    except:
        return None
    

def scraper(bairro):
    driver = webdriver.Chrome()

    url = 'https://www.quintoandar.com.br/comprar/imovel/'+bairro+'-sao-paulo-sp-brasil'
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    numero = soup.find("div", class_="Toolbar_title__hZZcF").text.split(" ")[0]

    driver.get('https://www.quintoandar.com.br/comprar/imovel/'+bairro+'-sao-paulo-sp-brasil')
    time.sleep(5)

    # for i in range(int(numero.replace('.', ''))//12):
    for i in range(30):
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
    try:
        rua = imovel.find("div", class_="Cozy__FindHouseCard-Container").text
        rua = rua.split("São Paulo")[0].split('\n\n')[-1].lstrip()
        rua = rua.split(",")[0]
        return rua
    except:
        return None

def find_preco_imovel(imovel):
    try:
        valor = imovel.find("div", class_="Cozy__FindHouseCard-Container").text
        valor = valor.split("R$")[1]
        return re.sub(r'\D', '', valor)
    except:
        return None

def find_m2_imovel(imovel):
    try:
        img_tag = imovel.find('img', class_='ProgressiveImage_image__1QoR0')
        alt_text = img_tag['alt']
        alt_text = alt_text.split("m²")[0].split(" ")
        return alt_text[-1]
    except:
        return None

def find_endereco(imovel):
    try:
        bairro = imovel.find("h2", class_="CozyTypography xih2fc _72Hu5c Ci-jp3").text
        bairro = bairro.replace('\n','')
        bairro = bairro.replace(" · ", ", ")
        bairro = bairro.lstrip()
        endereco = bairro.rstrip()
        return endereco
    except:
        return None

def find_bairro(imovel):
    try:
        bairro = imovel.find("h2", class_="CozyTypography xih2fc _72Hu5c Ci-jp3").text
        bairro = bairro.replace('\n','')
        bairro = bairro.replace(" · ", ", ")
        bairro = bairro.lstrip()
        bairro = bairro.rstrip()
        bairro = bairro.split(", ")[1]
        return bairro
    except:
        return None

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

def create_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cep TEXT,
    setor TEXT,
    rua TEXT,
    bairro TEXT,
    cidade TEXT,
    estado TEXT,
    regiao TEXT,
    preco FLOAT,
    m2 FLOAT,
    preco_m2 FLOAT
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
    try:
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
    except:
        print("Erro ao extrair dados do CEP")
        pass


# Analise de Resultados

def create_buffer(lat, lon, buffer_size_meters=500):
    # Aproximando 1 grau de latitude como 111.32 km
    buffer_degrees = buffer_size_meters / 111320  
    
    # Criando um quadrado centrado na coordenada fornecida
    buffer_box = box(lon - buffer_degrees / 2, lat - buffer_degrees / 2,
                     lon + buffer_degrees / 2, lat + buffer_degrees / 2)
    
    return buffer_box


# Função para estimar o preço médio por m² dentro do buffer
def estimate_price(address):
    # Passo 1: Geocodificar o endereço para obter latitude e longitude
    coordenadas = geocode_address(address)
    if not coordenadas:
        print("Endereço não encontrado.")
        return None
    
    lat, lon = coordenadas
    
    # Passo 2: Criar um buffer de 500 metros ao redor do ponto
    buffer = create_buffer(lat, lon)
    
    # Passo 3: Conectar ao banco de dados simplificado (dados_final)
    conn = sqlite3.connect('dados_final.db')
    cursor = conn.cursor()

    # Carregar todos os setores e suas coordenadas (centroides)
    cursor.execute('''
    SELECT setor, preco_medio_m2, lat, lon FROM dados_final
    ''')
    
    setores = cursor.fetchall()
    
    # Lista para armazenar preços dentro do buffer
    precos_buffer = []
    
    # Passo 4: Verificar quais setores estão dentro do buffer
    for setor, preco_medio_m2, setor_lat, setor_lon in setores:
        ponto_setor = Point(setor_lon, setor_lat)  # Criar ponto para o centro do setor
        if buffer.contains(ponto_setor):
            precos_buffer.append(preco_medio_m2)
    
    conn.close()
    
    # Passo 5: Calcular e retornar a média dos preços dentro do buffer
    if precos_buffer:
        media_preco_m2 = sum(precos_buffer) / len(precos_buffer)
        return media_preco_m2
    else:
        print("Nenhum setor encontrado dentro do buffer.")
        return None
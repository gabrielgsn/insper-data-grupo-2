import requests
from bs4 import BeautifulSoup
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from pprint import pprint
import sqlite3


def getDadosCEP(cep):
		url = (f'http://www.viacep.com.br/ws/{cep}/json')
		
		req = requests.get(url)
		if req.status_code == 200:
			dados_json = json.loads(req.text)
			return dados_json
		else:
			print('Erro ao buscar CEP')

def scraper(bairro):
    driver = webdriver.Chrome()

    driver.get('https://www.quintoandar.com.br/comprar/imovel/'+bairro+'-sao-paulo-sp-brasil')
    time.sleep(5)

    for i in range(9):
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

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

def add_data(cep, rua, bairro, cidade, estado, regiao, preco, m2, preco_m2):
    cursor.execute('''
    INSERT INTO data (cep, rua, bairro, cidade, estado, regiao, preco, m2, preco_m2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (cep, rua, bairro, cidade, estado, regiao, preco, m2, preco_m2))
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
        rua = find_rua_imovel(casa)
        preco_m2 = float(preco) / float(m2)
        
        # Check if the data already exists
        cursor.execute('''
        SELECT id FROM data 
        WHERE cep = ? AND bairro = ? AND preco = ? AND m2 = ?
        ''', (cep, bairro, preco, m2))
        
        if cursor.fetchone() is None:
            # Data doesn't exist, so insert it
            add_data(cep, rua, bairro, cidade, estado, regiao, preco, m2, preco_m2)

def precos_medios():
    cursor.execute('''
    SELECT bairro, AVG(preco_m2) AS preco_medio_m2
    FROM data
    GROUP BY bairro
    ''')
    return cursor.fetchall()
